import json
import traceback
from datetime import datetime, timezone

from django.conf import settings
from django.core.mail import EmailMessage

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status

from square.client import Client


class PaymentView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):

        try:
            user = request.user
            client = Client(
                access_token=settings.SQUAREUP_TOKEN,
                environment=settings.SQUAREUP_ENV,
            )

            req = json.loads(request.body.decode('utf8'))

            amount = float(req.get('amount'))
            total_cents = int(float(req.get('total')) * 100)
            payment = {
                'source_id': req.get('nonce'),
                'idempotency_key': req.get('key'),
                'amount_money': {'amount': total_cents, 'currency': 'USD'},
            }

            result = client.payments.create_payment(payment)

            if result.is_success():
                pmt = {
                    'date': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    'amount': amount
                }
                user.payments.append(pmt)
                user.save()

                try:
                    subject = 'Card Payment Received.'
                    t = float(req.get('total'))
                    a = float(req.get('amount'))
                    ct = "${:,.2f}".format(t)
                    ca = "${:,.2f}".format(a)
                    message = f'Thank you for your payment of {ct}! {ca} has been applied to your account.'
                    from_email = 'PilotAndy Aviation <automated@pilotandy.com>'
                    msg = EmailMessage(subject, message, from_email, [
                        str(user)], bcc=['andy@pilotandy.com'])
                    msg.content_subtype = "html"  # Main content is now text/html
                    msg.send()
                except:
                    print(traceback.format_exc())

                return Response('Payment accepted. Thank you!')
            elif result.is_error():
                return Response(result.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as exc:
            return Response(str(exc), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
