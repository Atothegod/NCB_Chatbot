from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import KYC, CreditBureauRequest
from .serializers import KYCSerializer, CreditBureauRequestSerializer


# -------------------------
# CREATE KYC
# -------------------------
@api_view(["POST"])
def create_kyc(request):

    serializer = KYCSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(["POST"])
def create_credit_request(request):

    kyc_id = request.data.get("kyc_id")

    if not kyc_id:
        return Response(
            {"error": "kyc_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        kyc = KYC.objects.get(id=kyc_id)

    except KYC.DoesNotExist:
        return Response(
            {"error": "KYC not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if kyc.kyc_status != "verified":
        return Response(
            {"error": "KYC not verified"},
            status=status.HTTP_400_BAD_REQUEST
        )

    existing = CreditBureauRequest.objects.filter(kyc=kyc).last()

    if existing:

        delivery_destination = None

        if existing.delivery_method == "email":
            delivery_destination = existing.email_delivery

        elif existing.delivery_method == "postal":
            delivery_destination = existing.postal_address

        return Response({
            "track_id": str(existing.track_id),
            "status": existing.status,
            "delivery_method": existing.delivery_method,
            "delivery_destination": delivery_destination,
            "created_at": existing.created_at
        })

    req = CreditBureauRequest.objects.create(kyc=kyc)

    delivery_destination = None

    if req.delivery_method == "email":
        delivery_destination = req.email_delivery

    elif req.delivery_method == "postal":
        delivery_destination = req.postal_address

    return Response({
        "track_id": str(req.track_id),
        "status": req.status,
        "delivery_method": req.delivery_method,
        "delivery_destination": delivery_destination,
        "created_at": req.created_at
    }, status=status.HTTP_201_CREATED)


# -------------------------
# TRACK REQUEST BY TRACK_ID
# -------------------------
@api_view(["GET"])
def track_request(request, track_id):

    try:
        req = CreditBureauRequest.objects.get(track_id=track_id)

    except CreditBureauRequest.DoesNotExist:
        return Response(
            {"error": "Request not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    delivery_destination = None

    if req.delivery_method == "email":
        delivery_destination = req.email_delivery

    elif req.delivery_method == "postal":
        delivery_destination = req.postal_address

    return Response({
        "track_id": str(req.track_id),
        "status": req.status,
        "delivery_method": req.delivery_method,
        "delivery_destination": delivery_destination,
        "created_at": req.created_at
    })


# -------------------------
# GET KYC STATUS
# -------------------------
@api_view(["GET"])
def get_kyc_status(request):

    kyc_id = request.query_params.get("kyc_id")

    if not kyc_id:
        return Response(
            {"error": "kyc_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        kyc = KYC.objects.get(id=kyc_id)

    except KYC.DoesNotExist:
        return Response(
            {"error": "KYC not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    return Response({
        "kyc_id": kyc.id,
        "kyc_status": kyc.kyc_status
    })


# -------------------------
# GET REQUEST BY USER
# -------------------------
@api_view(["GET"])
def get_request_by_user(request):

    kyc_id = request.query_params.get("kyc_id")

    if not kyc_id:
        return Response(
            {"error": "kyc_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    req = CreditBureauRequest.objects.filter(kyc_id=kyc_id).last()

    if not req:
        return Response(
            {"error": "No request found"},
            status=status.HTTP_404_NOT_FOUND
        )

    delivery_destination = None

    if req.delivery_method == "email":
        delivery_destination = req.email_delivery

    elif req.delivery_method == "postal":
        delivery_destination = req.postal_address

    return Response({
        "track_id": str(req.track_id),
        "status": req.status,
        "delivery_method": req.delivery_method,
        "delivery_destination": delivery_destination,
        "created_at": req.created_at
    })


# -------------------------
# SET DELIVERY METHOD
# -------------------------
@api_view(["POST"])
def set_delivery(request):

    track_id = request.data.get("track_id")
    method = request.data.get("delivery_method")

    if not track_id:
        return Response(
            {"error": "track_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        req = CreditBureauRequest.objects.get(track_id=track_id)

    except CreditBureauRequest.DoesNotExist:
        return Response(
            {"error": "Request not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if method == "email":

        email = request.data.get("email")

        if not email:
            return Response(
                {"error": "email is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        req.delivery_method = "email"
        req.email_delivery = email


    elif method == "postal":

        address = request.data.get("address")

        if not address:
            return Response(
                {"error": "address is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        req.delivery_method = "postal"
        req.postal_address = address


    else:
        return Response(
            {"error": "Invalid delivery method"},
            status=status.HTTP_400_BAD_REQUEST
        )

    req.save()

    delivery_destination = req.email_delivery or req.postal_address

    return Response({
        "track_id": str(req.track_id),
        "delivery_method": req.delivery_method,
        "delivery_destination": delivery_destination
    })


@api_view(["POST"])
def verify_track(request):

    track_id = request.data.get("track_id")
    email = request.data.get("email")

    if not track_id or not email:
        return Response(
            {"error": "track_id and email required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:

        req = CreditBureauRequest.objects.get(track_id=track_id)

    except CreditBureauRequest.DoesNotExist:

        return Response(
            {"error": "request not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # ตรวจสอบว่า email เป็นเจ้าของคำขอจริงไหม
    if req.kyc.email != email:

        return Response(
            {"error": "identity mismatch"},
            status=status.HTTP_403_FORBIDDEN
        )

    delivery_destination = req.email_delivery or req.postal_address

    return Response({
        "track_id": str(req.track_id),
        "status": req.status,
        "delivery_method": req.delivery_method,
        "delivery_destination": delivery_destination
    })