from sre_constants import SUCCESS
from django.conf import settings
from twilio.rest import Client
import random


class MessageHandler:
    phone_number=None
    otp=None
    
    def __init__(self,phone_number,otp)->None:
        self.phone_number=phone_number
        self.otp = otp
    
    def send_otp(self):
        print(self.otp,self.phone_number)
        client = Client(settings.ACCOUNT_SSID,settings.AUTH_TOKEN)

        message = client.messages \
        .create(
            body=f"your otp is {self.otp}.",
            from_='+12057821010',
            to=self.phone_number
        )
        print('SUCCESS')
        return True

