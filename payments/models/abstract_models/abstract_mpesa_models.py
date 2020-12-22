from django.db import models

from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _


class AbstractMpesaExpressRequest(models.Model):
    """
    Base class representing an STK-PUSH Request.
    """
    request_id = models.CharField(
        max_length=250, editable=False, unique=True,
        db_index=True, blank=True, null=True,
        help_text='System generated unique Identifier for this request')

    initialized_by = models.CharField(
        max_length=250, blank=True, null=True,
        help_text='This is the email address or username of the user who initialized this request if they are authenticated.')

    # MPESA FIELDS
    timestamp = models.CharField(max_length=250, null=True)  # when the stk push was done
    transaction_type = models.CharField(max_length=100, blank=True, null=True)
    amount = models.BigIntegerField(blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    account_reference = models.CharField(max_length=120, null=True, db_index=True)
    transaction_description = models.CharField(max_length=130, blank=True, null=True)
    merchant_request_id = models.CharField(
        max_length=254, blank=True, null=True, unique=True, db_index=True
    )
    checkout_request_id = models.CharField(
        max_length=254, blank=True, null=True, unique=True, db_index=True
    )
    response_code = models.CharField(max_length=250, blank=True, null=True)
    response_description = models.TextField(blank=True, null=True)
    customer_message = models.TextField(blank=True, null=True)
    callback_url = models.CharField(
        max_length=250, blank=True, null=True,
        help_text="The callback provided during the making of the request")

    business_shortcode = models.CharField(max_length=250, null=True)

    created_at = models.DateTimeField(_("Date created"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("Date updated"), auto_now=True, db_index=True)
    # STATUSES
    PROCESSING, SUCCESSFUL, FAILED, DISPUTED = (
        "Processing",
        "Successful",
        "Failed",
        "Disputed",
    )
    STATUS_CHOICES = (
        (SUCCESSFUL, _("Successful - Successful request")),
        (PROCESSING, _("Processing - Waiting for Mpesa Response")),
        (FAILED, _("Failed - Failed request")),
        (DISPUTED, _("Disputed - Payment has no Source")),
    )
    status = models.CharField(
        max_length=200, choices=STATUS_CHOICES, blank=True, null=True
    )  # choice field

    # Mpesa Response
    result_code = models.CharField(max_length=250, blank=True, null=True)
    result_description = models.TextField(blank=True, null=True)
    mpesa_receipt_number = models.CharField(
        max_length=254, blank=True, null=True
    )
    transaction_date = models.CharField(max_length=150, blank=True, null=True)
    # when the callback came back
    password = models.CharField(
        max_length=250, blank=True, null=True,
        help_text='base64.encode the Shortcode + Passkey + Timestamp')

    response_json = models.TextField(blank=True, null=True)
    # This is the json response after a successful stkpush call

    result_json = models.TextField(blank=True, null=True)
    # Store the Json Result from Safaricom from the callback
    # Regardress of being successful or failed.

    received_callback = models.BooleanField(default=False)
    # When we receive the callback we check this to true
    # Regardless of the txn being successful or failed

    queried = models.BooleanField(default=False)
    # If we don't receive the callback we do a
    # query to the safaricom API

    date_queried = models.DateTimeField(blank=True, null=True)
    # If we do a query about the txn record,log when it was queried

    query_json = models.TextField(blank=True, null=True)
    # If we do a query we need to save the query response dict
    # that we get from safaricom

    class Meta:
        abstract = True
        verbose_name = _("Mpesa Express Payment Request")
        verbose_name_plural = _("Mpesa Express Payments Requests")
        ordering = ["-updated_at", "-created_at"]

    def __str__(self):
        return str(self.request_id)

    def save(self, *args, **kwargs):
        if not self.request_id:
            self.request_id = self.__class__.generate_request_id()
        super().save(*args, **kwargs)

    @classmethod
    def generate_request_id(cls, length=77):
        """
        Generate a unique request id for this MpesaRequest.
        """
        while True:
            new_request_id = get_random_string(length=length)
            if not cls._default_manager.filter(request_id=new_request_id).exists():
                return new_request_id

    def receipt(self):
        """Return the mpesa_receipt_number if it exists."""
        return self.mpesa_receipt_number if self.mpesa_receipt_number else None

    def get_request_id(self):
        return self.request_id
