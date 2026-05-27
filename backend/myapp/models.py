from django.db import models
import uuid


class KYC(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("verified", "Verified"),
        ("rejected", "Rejected"),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)

    kyc_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class CreditBureauRequest(models.Model):

    DELIVERY_CHOICES = [
        ("email", "Email"),
        ("postal", "Postal"),
    ]

    STATUS_CHOICES = [
        ("requested", "Requested"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("rejected", "Rejected"),
    ]

    track_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    kyc = models.ForeignKey(
        KYC,
        on_delete=models.CASCADE,
        related_name="requests"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="requested"
    )

    delivery_method = models.CharField(
        max_length=10,
        choices=DELIVERY_CHOICES,
        null=True,
        blank=True
    )

    email_delivery = models.EmailField(
        null=True,
        blank=True
    )

    postal_address = models.TextField(
        null=True,
        blank=True
    )

    document_url = models.URLField(
        blank=True,
        null=True
    )

    admin_note = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.track_id} - {self.status}"