from rest_framework import serializers
from .models import KYC, CreditBureauRequest

class KYCSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYC
        fields = "__all__"


class CreditBureauRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditBureauRequest
        fields = "__all__"