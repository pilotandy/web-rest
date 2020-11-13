import io
import os
import base64
import random
from PIL import Image, ImageDraw, ImageFont


class ImageTool():

    palettes = [
        {'bg': (233, 30, 99), 'fg': (255, 255, 255)},
        {'bg': (156, 39, 176), 'fg': (255, 255, 255)},
        {'bg': (103, 58, 183), 'fg': (255, 255, 255)},
        {'bg': (63, 81, 181), 'fg': (255, 255, 255)},
        {'bg': (33, 150, 243), 'fg': (255, 255, 255)},
        {'bg': (3, 169, 244), 'fg': (0, 0, 0)},
        {'bg': (0, 188, 212), 'fg': (0, 0, 0)},
        {'bg': (0, 150, 136), 'fg': (255, 255, 255)},
        {'bg': (76, 175, 80), 'fg': (255, 255, 255)},
        {'bg': (139, 195, 74), 'fg': (0, 0, 0)},
        {'bg': (205, 220, 57), 'fg': (0, 0, 0)},
        {'bg': (255, 235, 59), 'fg': (0, 0, 0)},
        {'bg': (255, 193, 7), 'fg': (0, 0, 0)},
        {'bg': (255, 152, 0), 'fg': (0, 0, 0)},
        {'bg': (255, 87, 34), 'fg': (255, 255, 255)},
        {'bg': (121, 85, 72), 'fg': (255, 255, 255)},
        {'bg': (158, 158, 158), 'fg': (0, 0, 0)},
        {'bg': (96, 125, 139), 'fg': (255, 255, 255)},
    ]

    @staticmethod
    def genProfileImage(firstname, lastname):

        initials = firstname[0].upper() + lastname[0].upper()

        # get a random palette
        i = random.randint(0, len(ImageTool.palettes) - 1)
        pal = ImageTool.palettes[i]

        # The actual SVG
        svg = """
            <svg xmlns="http://www.w3.org/2000/svg" height="10em" width="10em">
                <rect width="10em" height="10em" style="fill:rgb{}" />
                <text font-family="monospace" font-size="6em" fill="rgb{}"
                      x="50%" y="54%" text-anchor="middle" alignment-baseline="middle">{}</text>
            </svg>
        """.format(str(pal['bg']), str(pal['fg']), initials)

        # Image to base64
        buffer = io.BytesIO()

        buffer.write(svg.encode('utf8'))
        img_data = base64.b64encode(buffer.getvalue()).decode('utf8')
        img_str = 'data:image/svg+xml;base64,'

        return img_str + img_data

    @staticmethod
    def setProfileImage(imageUri):
        data64 = imageUri.split(',')[1]
        data = io.BytesIO()
        data.write(base64.b64decode(data64))
        data.seek(0)
        img = Image.open(data)
        w, h = img.size
        if(w == 300 and h == 300):
            return imageUri
        if(w > h):
            ratio = (w/h)
            h = 300
            w = int(round(ratio * h))
            t = 0
            l = int(round((w - 300) / 2))
            b = 300
            r = l + 300
        elif(w < h):
            ratio = (h/w)
            w = 300
            h = int(round(ratio * w))
            t = int(round((h - 300) / 2))
            l = 0
            b = t + 300
            r = 300
        else:
            h = 300
            w = 300
            t = 0
            l = 0
            b = 300
            r = 300

        img = img.resize((w, h), Image.ANTIALIAS)
        img = img.crop((l, t, r, b))
        data = io.BytesIO()
        img.save(data, "PNG")
        data64 = base64.b64encode(data.getvalue())
        return u'data:img/png;base64,'+data64.decode('utf-8')
