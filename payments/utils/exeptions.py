class PaymentError(Exception):
    pass


class MpesaError(PaymentError):
    pass


class InvalidTransactionAmount(MpesaError):
    pass
