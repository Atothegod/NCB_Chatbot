from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views

urlpatterns = [

    path("kyc/create/", views.create_kyc),
    path("kyc/status/", views.get_kyc_status),

    path("credit-request/create/", views.create_credit_request),
    path("credit-request/status/<uuid:track_id>/", views.track_request),
    path("credit-request/by-user/", views.get_request_by_user),
    path("credit-request/delivery/", views.set_delivery),

    path("credit-request/verify-track/", views.verify_track),
]