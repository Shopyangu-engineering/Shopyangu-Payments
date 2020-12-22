import base64
import requests
from requests.auth import HTTPBasicAuth
from .base import MpesaBase

from decouple import config


class MpesaExpress(MpesaBase):

    def __init__(self, model, app_key=None, app_secret=None, short_code=None, passkey=None, **kwargs):
        super().__init__(**kwargs)
        self.stk_push_endpoint = "{base_url}{stk_uri}".format(
            base_url=self.base_safaricom_url, stk_uri="/mpesa/stkpush/v1/processrequest")
        self.app_key = app_key if app_key else self.get_consumer_key()
        self.app_secret = app_secret if app_secret else self.get_consumer_secret()
        self.short_code = short_code if short_code else self.get_short_code()
        self.model = model
        self.authentication_token = self.authenticate()

    def get_consumer_key(self):
        consumer_key = config("C2B_ONLINE_PASSKEY")
        return consumer_key

    def get_consumer_secret(self):
        """
        Return mpesa consumer_secret from env
        """
        consumer_secret = config("mpesa_consumer_secret")
        return consumer_secret

    def get_short_code(self):
        """
        Return Safaricom short code
        """
        short_code = config("C2B_ONLINE_SHORT_CODE")
        return short_code

    def get_passkey(self):
        """
        Return mpesa passkey from env
        """
        key = config("mpesa_passkey")
        return key

    def authenticate(self):
        """
        To make Mpesa API calls, you will need to authenticate your app. This method is used to fetch the access token
        required by Mpesa. Mpesa supports client_credentials grant type. To authorize your API calls to Mpesa,
        you will need a Basic Auth over HTTPS authorization token. The Basic Auth string is a base64 encoded string
        of your app's client key and client secret.

        **Returns:**
                - access_token (str): This token is to be used with the Bearer header for further API calls to Mpesa.
        """
        r = requests.get(self.generate_token_url, auth=HTTPBasicAuth(self.app_key, self.app_secret))
        token = r.json()['access_token']
        return token

    def headers(self):
        return {'Authorization': 'Bearer {0}'.format(self.authentication_token), 'Content-Type': "application/json"}

    def to_base64(self, timestamp):
        """
        Encodes the  given string to base64
        :param timestamp: str to encode
        :return: base64 encoded str
        """
        short_code = self.get_short_code()
        passkey = self.get_passkey()
        the_date = str(timestamp)
        data = short_code + passkey + the_date
        final_result = base64.urlsafe_b64encode(data.encode("UTF-8")).decode("ascii")

        return final_result
