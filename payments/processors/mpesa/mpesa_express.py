import base64
import functools
import requests

from requests.auth import HTTPBasicAuth
from decimal import Decimal as D
from decouple import config
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from .base import MpesaBase
from payments.utils.http import post

from payments.utils.exeptions import InvalidTransactionAmount



class MpesaExpress(MpesaBase):

    def __init__(self, model=None, app_key=None, app_secret=None, short_code=None, passkey=None, **kwargs):
        super().__init__(**kwargs)
        self.stk_push_endpoint = "{base_url}{stk_uri}".format(
            base_url=self.base_safaricom_url, stk_uri="/mpesa/stkpush/v1/processrequest")
        self.app_key = app_key if app_key else self.get_consumer_key()
        self.app_secret = app_secret if app_secret else self.get_consumer_secret()
        self.short_code = short_code if short_code else self.get_short_code()

        if not model:
            from payments.models import MpesaExpressRequest
            model = MpesaExpressRequest
        self.model = model
        self.authentication_token = self.authenticate

    def get_consumer_key(self):
        consumer_key = config("C2B_ONLINE_CONSUMER_KEY")
        return consumer_key

    def get_consumer_secret(self):
        """
        Return mpesa consumer_secret from env
        """
        consumer_secret = config("C2B_CONSUMER_SECRET")
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
        key = config("C2B_ONLINE_PASSKEY")
        return key

    def get_stk_callback(self):
        callback = config('C2B_ONLINE_CHECKOUT_CALLBACK_URL')
        return callback

    @property
    @functools.lru_cache()
    def authenticate(self):
        """
        To make Mpesa API calls, you will need to authenticate your app. This method is used to fetch the access token
        required by Mpesa. Mpesa supports client_credentials grant type. To authorize your API calls to Mpesa,
        you will need a Basic Auth over HTTPS authorization token. The Basic Auth string is a base64 encoded string
        of your app's client key and client secret.

        **Returns:**
                - access_token (str): This token is to be used with the Bearer header for further API calls to Mpesa.
        """
        if self.authentication_token is None:
            r = requests.get(self.generate_token_url, auth=HTTPBasicAuth(self.app_key, self.app_secret))
            token = r.json()['access_token']
            self.authentication_token = token
            return token
        else:
            return self.authentication_token

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

    def initialize_stk_push(self, **kwargs):
        """
        This method uses Mpesa's Express API to initiate online payment on behalf of a customer..
        """
        response = {
            "is_successfull": False,
            "charge_obj": None,
            "mpesa_response_status_code": None,
            "message": None,
            "mpesa_response": None
        }
        expected_keys = ["Amount", "PhoneNumber", "AccountReference"]
        # allowed_null = ["CallBackURL", "InitializedBy", "BusinessShortCode", "IsPaybill", "TransactionDesc", "AccountReference"]

        payload_data = self.process_kwargs(expected_keys, expecting_more_kwargs=True, **kwargs)
        payload = payload_data[0] if type(payload_data) == list else payload_data
        extra_kwargs = payload_data[1] if type(payload_data) == list else None

        Amount = payload.get('Amount')
        PhoneNumber = payload.get('PhoneNumber')
        AccountReference = payload.get('AccountReference')
        BusinessShortCode = extra_kwargs.get('BusinessShortCode') if extra_kwargs and 'BusinessShortCode' in extra_kwargs else self.get_short_code()
        IsPaybill = extra_kwargs.get('IsPaybill') if extra_kwargs and 'IsPaybill' in extra_kwargs else True
        CallBackURL = extra_kwargs.get('CallBackURL') if extra_kwargs and 'CallBackURL' in extra_kwargs else self.get_stk_callback()
        InitializedBy = extra_kwargs.get('InitializedBy') if extra_kwargs and 'InitializedBy' in extra_kwargs else None
        TransactionDesc = extra_kwargs.get('TransactionDesc') if extra_kwargs and 'TransactionDesc' in extra_kwargs else "Stk Push of {amount} to {phone_number}".format(
            amount=Amount, phone_number=PhoneNumber)

        TransactionType = "CustomerPayBillOnline" if IsPaybill else "CustomerBuyGoodsOnline"

        current_time = self.get_current_formated_time()
        
        password = self.to_base64(current_time)

        mpesa_payload = {
            "BusinessShortCode": BusinessShortCode,
            "Password": password,
            "Timestamp": current_time,
            "TransactionType": TransactionType,
            "Amount": Amount,
            "PartyA": PhoneNumber,
            "PartyB": BusinessShortCode,
            "PhoneNumber": PhoneNumber,
            "CallBackURL": CallBackURL,
            "AccountReference": AccountReference,
            "TransactionDesc": TransactionDesc
        }

        try:
            r = post(url=self.stk_push_endpoint, headers=self.headers(), data=mpesa_payload)

            print(r, "The R")
            print(r.status_code, "status code")
            print(r.json(), "The json")
            # print(r, "The R")

            if r.status_code == 200:
                with transaction.atomic():
                    new_stk_request = self.model.objects.record_response(
                        
                    )

        except Exception as err:
            print(err)

        return r.json()

    def handle_stk_response(self, **kwargs):
        """Handle a successful STK Response after intializing the request."""
        expected_keys = [
            "InitializedBy", "Timestamp", "Amount", "PhoneNumber",
            "IsPaybill", "BusinessShortCode", "TransactionType",
            "CallBackURL", "TransactionDesc", "AccountReference",
            ""
            ]
