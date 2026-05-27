import requests
import os
from memory import get_memory

BACKEND = os.getenv("BACKEND_URL")


# -------------------------
# KYC STATUS
# -------------------------
def get_kyc_status():

    memory = get_memory()

    kyc_id = memory.get("kyc_id")

    if not kyc_id:
        return {
            "type": "kyc_status",
            "status": "not_found"
        }

    try:

        r = requests.get(
            f"{BACKEND}/kyc/status/",
            params={"kyc_id": kyc_id}
        )

        if r.status_code != 200:
            return {
                "type": "kyc_status",
                "status": "error"
            }

        data = r.json()

        return {
            "type": "kyc_status",
            "status": data.get("kyc_status")
        }

    except Exception:

        return {
            "type": "kyc_status",
            "status": "error"
        }


# -------------------------
# CREATE CREDIT REQUEST
# -------------------------
def create_credit_request():

    memory = get_memory()

    kyc_id = memory.get("kyc_id")

    if not kyc_id:
        return {
            "type": "error",
            "message": "kyc_required"
        }

    # -------------------------
    # ถ้ามี request อยู่แล้ว → sync จาก backend
    # -------------------------
    if memory.get("track_id"):
        return check_status()

    try:

        r = requests.post(
            f"{BACKEND}/credit-request/create/",
            json={"kyc_id": kyc_id},
            timeout=5
        )

        if r.status_code not in [200, 201]:
            return {
                "type": "error",
                "message": "request_failed"
            }

        data = r.json()

        track_id = data.get("track_id")

        memory["track_id"] = track_id

        delivery_method = data.get("delivery_method")

        delivery_destination = (
            data.get("delivery_destination")
            or data.get("email_delivery")
            or data.get("postal_address")
        )

        memory["delivery_method"] = delivery_method
        memory["delivery_destination"] = delivery_destination

        return {
            "type": "credit_request_created",
            "track_id": track_id,
            "status": data.get("status"),
            "delivery_method": delivery_method,
            "delivery_destination": delivery_destination
        }

    except Exception:

        return {
            "type": "error",
            "message": "request_failed"
        }


# -------------------------
# CHECK REQUEST STATUS
# -------------------------
def check_status():

    memory = get_memory()

    kyc_id = memory.get("kyc_id")

    if not kyc_id:
        return {
            "type": "error",
            "message": "kyc_required"
        }

    try:

        r = requests.get(
            f"{BACKEND}/credit-request/by-user/",
            params={"kyc_id": kyc_id}
        )

        if r.status_code != 200:
            return {
                "type": "error",
                "message": "status_error"
            }

        data = r.json()

        track_id = data.get("track_id")
        status = data.get("status")
        delivery_method = data.get("delivery_method")

        delivery_destination = (
            data.get("delivery_destination")
            or data.get("email_delivery")
            or data.get("postal_address")
        )

        memory["track_id"] = track_id
        memory["delivery_method"] = delivery_method
        memory["delivery_destination"] = delivery_destination

        return {
            "type": "request_status",
            "track_id": track_id,
            "status": status,
            "delivery_method": delivery_method,
            "delivery_destination": delivery_destination
        }

    except Exception:

        return {
            "type": "error",
            "message": "status_error"
        }


# -------------------------
# SET DELIVERY METHOD
# -------------------------
def set_delivery_method(method: str, value: str):

    memory = get_memory()

    track_id = memory.get("track_id")

    if not track_id:
        return {
            "type": "error",
            "message": "no_active_request"
        }

    payload = {
        "track_id": track_id,
        "delivery_method": method
    }

    if method == "email":
        payload["email"] = value

    elif method == "postal":
        payload["address"] = value

    else:
        return {
            "type": "error",
            "message": "invalid_delivery_method"
        }

    try:

        r = requests.post(
            f"{BACKEND}/credit-request/delivery/",
            json=payload
        )

        if r.status_code != 200:
            return {
                "type": "error",
                "message": "delivery_set_failed"
            }

        memory["delivery_method"] = method
        memory["delivery_destination"] = value

        return {
            "type": "delivery_set",
            "delivery_method": method,
            "delivery_destination": value,
            "track_id": track_id
        }

    except Exception:

        return {
            "type": "error",
            "message": "delivery_set_failed"
        }


# -------------------------
# VERIFY TRACK ID + EMAIL
# -------------------------
def verify_track(track_id: str, email: str):

    try:

        r = requests.post(
            f"{BACKEND}/credit-request/verify-track/",
            json={
                "track_id": track_id,
                "email": email
            }
        )

        if r.status_code != 200:
            return {
                "type": "error",
                "message": "identity_verification_failed"
            }

        data = r.json()

        memory = get_memory()

        memory["track_id"] = data.get("track_id")
        memory["delivery_method"] = data.get("delivery_method")
        memory["delivery_destination"] = data.get("delivery_destination")

        return {
            "type": "request_status",
            "track_id": data.get("track_id"),
            "status": data.get("status"),
            "delivery_method": data.get("delivery_method"),
            "delivery_destination": data.get("delivery_destination")
        }

    except Exception:

        return {
            "type": "error",
            "message": "identity_verification_failed"
        }