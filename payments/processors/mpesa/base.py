import datetime


class MpesaBase:

    def __init__(self, is_sandbox_env=True, **kwargs):
        self.is_sandbox_env = is_sandbox_env
        self.base_safaricom_url = self.get_base_safaricom_url()
        self.authentication_token = None
        self.generate_token_url = "{base_url}{authenticate_uri}".format(
            base_url=self.base_safaricom_url, authenticate_uri="/oauth/v1/generate?grant_type=client_credentials")

        super().__init__(**kwargs)

    def get_base_safaricom_url(self):
        live_url = "https://api.safaricom.co.ke"
        sandbox_url = "https://sandbox.safaricom.co.ke"

        return sandbox_url if self.is_sandbox_env else live_url

    def authenticate(self):
        raise NotImplementedError

    def process_kwargs(self, expected_keys, expecting_more_kwargs=False, ** kwargs):
        """
        Check for any expected but missing keyword arguments
        and raise a MissingArgumentError and check if unexpected keyword arguments are provided
        and raise a InvalidArgumentError else return the keywords arguments
        repackaged in a dictionary i.e the payload.
        """
        payload = {}
        for key in expected_keys:
            value = kwargs.pop(key, False)
            if not value:
                raise ValueError("Missing keyword argument: %s" % key)
            else:
                payload[key] = value

        if len(kwargs.keys()) != 0:
            if expecting_more_kwargs:
                final_payload = []
                final_payload.extend([payload, kwargs])
                return final_payload
            else:
                raise ValueError('Unepxected kwargs provided: %s' % list(kwargs.keys()))

        return payload

    def get_current_formated_time(self):
        """RReturn the current time formated based on Y/M/D/H/M/S """
        return datetime.datetime.now().strftime("%Y%m%d%H%M%S")
