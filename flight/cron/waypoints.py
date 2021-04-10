import io
import os
import re
import sys
import shutil
import logging
import zipfile
import requests
import traceback
from datetime import date

from django_cron import CronJobBase, Schedule
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D, Distance
from bs4 import BeautifulSoup

from flight.models import Cycle, Airport, Nav

URL = 'https://www.faa.gov/air_traffic/flight_info/aeronav/aero_data/NASR_Subscription/'


def dms_dd(dms):
    dms = dms.rstrip()
    parts = dms.split('-')
    dd = float(parts[0]) + (float(parts[1]) / 60.0) + \
        (float(parts[2][:-1])/3600.0)
    if dms[-1] == 'S' or dms[-1] == 'W':
        dd *= -1
    return dd


class ProcessAPT():
    def __init__(self, cycle):
        self.cycle = cycle
        self.parsers = {
            'APT': self.parse_APT,
        }

    def parse_APT(self, line):
        ICAO = line[27:31].rstrip()
        ICAO2 = line[1210:1214]
        if len(ICAO2.rstrip()) > 0:
            ICAO = ICAO2
        Type = line[14:22].rstrip()
        Name = line[133:183].rstrip()
        Latitude = dms_dd(line[523:537])
        Longitude = dms_dd(line[550:565])
        Elevation = float(line[578:585])

        if Type == 'AIRPORT':
            airport, created = Airport.objects.get_or_create(icao=ICAO,
                                                             defaults={
                                                                 'name': Name,
                                                                 'fix': GEOSGeometry(f'POINT({Latitude} {Longitude})', srid=3857),
                                                                 'elevation': Elevation
                                                             })
            airport.name = Name
            airport.fix = GEOSGeometry(
                f'POINT({Latitude} {Longitude})', srid=3857)
            airport.elevation = Elevation
            airport.save()

    def run(self, fileHandle):

        for line in fileHandle:
            line = line.decode('cp1252')
            key = line[0:3]
            if key in self.parsers:
                parser = self.parsers[key]
                if parser:
                    parser(line)

        Cycle.objects.update_or_create(name='APT', cycle=self.cycle)


class ProcessNAV():
    def __init__(self, cycle):
        self.cycle = cycle
        self.parsers = {
            'NAV1': self.parse_NAV1,
        }

    def parse_NAV1(self, line):
        ICAO = line[4:8].rstrip()
        Type = line[8:28].rstrip()
        Name = line[42:72].rstrip()
        Class = line[281:292].rstrip()
        Latitude = dms_dd(line[371:385])
        Longitude = dms_dd(line[396:410])
        Elevation = line[472:479].rstrip()
        Freq = line[533:539].rstrip()
        Status = line[766:796].rstrip()
        if Elevation != '':
            Elevation = float(Elevation)
        else:
            Elevation = 0.0

        nav, created = Nav.objects.get_or_create(icao=ICAO,
                                                 defaults={
                                                     'name': Name,
                                                     'type': Type,
                                                     'fix': GEOSGeometry(f'POINT({Latitude} {Longitude})', srid=3857),
                                                     'elevation': Elevation,
                                                     'details': {}
                                                 })
        nav.name = Name
        nav.type = Type
        nav.fix = GEOSGeometry(f'POINT({Latitude} {Longitude})', srid=3857)
        nav.elevation = Elevation
        nav.details = {
            'status': Status,
            'class': Class,
            'freq': Freq,
        }
        nav.save()

    def run(self, fileHandle):

        for line in fileHandle:
            line = line.decode('cp1252')
            key = line[0:4]
            if key in self.parsers:
                parser = self.parsers[key]
                if parser:
                    parser(line)

        Cycle.objects.update_or_create(name='APT', cycle=self.cycle)


dispatch = {
    'APT': ProcessAPT,
    'NAV': ProcessNAV,
}


def getCurrentCycle():

    # find the uri and get the cycle
    req = requests.get(URL)
    assert req.status_code == 200, 'Could not get HTML from FAA Website.'
    parsed_html = BeautifulSoup(req.text, features="html.parser")
    link = parsed_html.body.find(
        "h2", string='Current').findNext('ul').find('a')
    uri = link.attrs['href']
    uri_date = re.search(r'(\d{4})-(\d\d)-(\d\d)$', uri)
    assert uri_date is not None, 'Could not extract cycle from URI.'
    cycle = date(int(uri_date[1]), int(uri_date[2]), int(uri_date[3]))

    # Get the zip link
    req = requests.get(URL + uri)
    assert req.status_code == 200, 'Could not get zip link from FAA Website.'
    parsed_html = BeautifulSoup(req.text, features="html.parser")
    link = parsed_html.body.find("a", href=re.compile(
        r'28DaySubscription_Effective'), string='Download')
    zip_link = link.attrs['href']
    return cycle, zip_link


def getCurrentZip(uri):
    req = requests.get(uri, stream=True)
    assert req.status_code == 200, 'Could not download zip file from FAA Website.'
    zipobj = io.BytesIO(req.raw.data)
    return zipobj


def getTestZip():
    with open('/home/andy/web/pilotandy/work/28DaySubscription_Effective_2020-11-05.zip', 'rb') as fh:
        zipobj = io.BytesIO(fh.read())
        zipobj.seek(0)
    return zipobj


def processZip(zipobj, cycle):
    with zipfile.ZipFile(zipobj, 'r') as zip_ref:
        filenames = zip_ref.namelist()
        for filename in filenames:
            if '/' not in filename:
                key = os.path.splitext(filename)[0]
                if key in dispatch and dispatch[key] is not None:
                    with zip_ref.open(filename, 'r') as fh:
                        klass = dispatch[key](cycle)
                        klass.run(fh)


class UpdateWaypoints(CronJobBase):
    RUN_EVERY_MINS = 1440  # every day

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'flight.update_waypoints'

    def do(self):
        try:
            cycle, uri = getCurrentCycle()
            zipobj = getCurrentZip(uri)
            # zipobj = getTestZip()
            processZip(zipobj, cycle)
            return f'Cycle: {cycle}, Source: {uri}'
        except:
            print(traceback.format_exc())
