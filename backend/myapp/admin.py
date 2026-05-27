from django.contrib import admin
from .models import KYC, CreditBureauRequest


@admin.register(KYC)
class KYCAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "kyc_status",
        "created_at",
    )

    search_fields = (
        "first_name",
        "last_name",
        "email",
        "phone_number",
    )

    list_filter = ("kyc_status",)


@admin.register(CreditBureauRequest)
class CreditBureauRequestAdmin(admin.ModelAdmin):

    list_display = (
        "track_id",
        "kyc",
        "status",
        "created_at",
        "updated_at",
    )

    list_filter = ("status",)

    search_fields = (
        "track_id",
        "kyc__first_name",
        "kyc__last_name",
    )