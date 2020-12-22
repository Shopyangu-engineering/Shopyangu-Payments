from django.contrib import admin

from .models import MpesaExpressRequest


class MpesaExpressRequestAdmin(admin.ModelAdmin):
    list_display = [
        'request_id',
        'created_at'
    ]
    search_fields = [
        'request_id',
        'initialized_by',
        'phone_number',
        'mpesa_receipt_number'
    ]


admin.site.register(MpesaExpressRequest, MpesaExpressRequestAdmin)
