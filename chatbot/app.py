import chainlit as cl
import requests
import os
import json

from agent import react_agent
from memory import get_memory

BACKEND = os.getenv("BACKEND_URL")


# -------------------------
# KYC FORM
# -------------------------
async def collect_kyc():

    first = await cl.AskUserMessage(
        content="กรุณากรอกชื่อจริง",
        timeout=300
    ).send()

    last = await cl.AskUserMessage(
        content="กรุณากรอกนามสกุล",
        timeout=300
    ).send()

    phone = await cl.AskUserMessage(
        content="กรุณากรอกเบอร์โทรศัพท์",
        timeout=300
    ).send()

    email = await cl.AskUserMessage(
        content="กรุณากรอกอีเมล",
        timeout=300
    ).send()

    r = requests.post(
        f"{BACKEND}/kyc/create/",
        json={
            "first_name": first["output"],
            "last_name": last["output"],
            "phone_number": phone["output"],
            "email": email["output"]
        }
    )

    if r.status_code in [200, 201]:

        data = r.json()

        memory = get_memory()
        memory["kyc_id"] = data["id"]

        await cl.Message(
            content="✅ ส่งข้อมูล KYC เรียบร้อยแล้ว\nกรุณารอการตรวจสอบจากเจ้าหน้าที่"
        ).send()

    else:

        await cl.Message(
            content=f"❌ เกิดข้อผิดพลาดในการส่ง KYC: {r.text}"
        ).send()


# -------------------------
# DELIVERY FORM
# -------------------------
async def collect_delivery(track_id):

    method = await cl.AskUserMessage(
        content=(
            "ต้องการรับรายงานเครดิตด้วยวิธีใด?\n\n"
            "email → รับทางอีเมล\n"
            "postal → รับทางไปรษณีย์"
        ),
        timeout=300
    ).send()

    method = method["output"].lower()

    if method == "email":

        email = await cl.AskUserMessage(
            content="กรุณากรอกอีเมลสำหรับรับรายงาน",
            timeout=300
        ).send()

        payload = {
            "track_id": track_id,
            "delivery_method": "email",
            "email": email["output"]
        }

    elif method == "postal":

        address = await cl.AskUserMessage(
            content="กรุณากรอกที่อยู่สำหรับจัดส่ง",
            timeout=300
        ).send()

        payload = {
            "track_id": track_id,
            "delivery_method": "postal",
            "address": address["output"]
        }

    else:

        await cl.Message(
            content="❌ กรุณาพิมพ์ email หรือ postal"
        ).send()
        return

    r = requests.post(
        f"{BACKEND}/credit-request/delivery/",
        json=payload
    )

    if r.status_code == 200:

        memory = get_memory()
        memory["delivery_method"] = payload["delivery_method"]
        memory["delivery_destination"] = payload.get("email") or payload.get("address")

        await cl.Message(
            content="✅ บันทึกวิธีการจัดส่งเรียบร้อยแล้ว"
        ).send()

    else:

        await cl.Message(
            content="❌ ไม่สามารถบันทึกวิธีการจัดส่งได้"
        ).send()


# -------------------------
# CHAT START
# -------------------------
@cl.on_chat_start
async def start():

    get_memory()

    await cl.Message(
        content=(
            "👋 สวัสดี\n\n"
            "ฉันคือผู้ช่วยเครดิตบูโร\n\n"
            "คุณสามารถ\n"
            "- ขอรายงานเครดิต\n"
            "- ตรวจสอบสถานะคำขอ"
        )
    ).send()





@cl.on_message
async def main(message: cl.Message):

    try:

        memory = get_memory()

        pred = react_agent(question=message.content)
        answer = pred.answer

        # -------------------------
        # Parse JSON if string
        # -------------------------
        if isinstance(answer, str):
            try:
                answer = json.loads(answer)
            except:
                pass

        print("AGENT ANSWER:", answer)

        # -------------------------
        # HANDLE TOOL RESPONSES
        # -------------------------
        if isinstance(answer, dict):

            # -------------------------
            # KYC STATUS
            # -------------------------
            if answer.get("type") == "kyc_status":

                status = answer.get("status")

                if status == "not_found":

                    await cl.Message(
                        content="ไม่พบข้อมูล KYC ของคุณ กรุณายืนยันตัวตนก่อนใช้งาน"
                    ).send()

                    await collect_kyc()
                    return

                if status == "pending":

                    await cl.Message(
                        content="KYC ของคุณกำลังอยู่ระหว่างการตรวจสอบ"
                    ).send()
                    return

                if status == "verified":

                    await cl.Message(
                        content="KYC ผ่านแล้ว คุณสามารถขอรายงานเครดิตได้"
                    ).send()
                    return


            # -------------------------
            # CREDIT REQUEST CREATED
            # -------------------------
            if answer.get("type") == "credit_request_created":

                track_id = answer["track_id"]
                memory["track_id"] = track_id

                await cl.Message(
                    content=(
                        f"✅ สร้างคำขอรายงานเครดิตเรียบร้อย\n\n"
                        f"Track ID: {track_id}\n\n"
                        "กรุณาเลือกวิธีการจัดส่งรายงาน"
                    )
                ).send()

                await collect_delivery(track_id)
                return


            # -------------------------
            # DELIVERY SET (NEW)
            # -------------------------
            if answer.get("type") == "delivery_set":

                destination = answer.get("delivery_destination")

                await cl.Message(
                    content=f"✅ ตั้งค่าการจัดส่งเรียบร้อย รายงานจะถูกส่งไปที่ {destination}"
                ).send()

                return


            # -------------------------
            # REQUEST STATUS
            # -------------------------
            if answer.get("type") == "request_status":

                status = answer.get("status")
                delivery = answer.get("delivery_method")
                destination = answer.get("delivery_destination")

                track_id = answer["track_id"]
                memory["track_id"] = track_id

                if not delivery:

                    await cl.Message(
                        content="คุณยังไม่ได้กำหนดวิธีจัดส่งรายงาน"
                    ).send()

                    await collect_delivery(track_id)
                    return

                if status == "completed":

                    await cl.Message(
                        content=(
                            "📄 รายงานเครดิตของคุณพร้อมแล้ว\n\n"
                            f"Track ID: {track_id}\n"
                            f"วิธีจัดส่ง: {delivery}\n"
                            f"จะส่งไปที่: {destination}"
                        )
                    ).send()

                    return

                await cl.Message(
                    content=(
                        f"สถานะคำขอ: {status}\n"
                        f"วิธีจัดส่ง: {delivery}\n"
                        f"ปลายทาง: {destination}"
                    )
                ).send()

                return


        # -------------------------
        # TEXT FALLBACK
        # -------------------------
        text = str(answer)

        if "KYC" in text and "ไม่พบ" in text:

            await cl.Message(
                content="กรุณายืนยันตัวตน (KYC) ก่อนดำเนินการยื่นเรื่องขอรายงานเครดิตบูโร หรือ ตรวจสอบสถานะคำขอค่ะ"
            ).send()

            await collect_kyc()
            return

        await cl.Message(content=text).send()

    except Exception as e:

        print("AGENT ERROR:", e)

        await cl.Message(
            content="❌ เกิดข้อผิดพลาดในระบบ"
        ).send()
