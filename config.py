import os
import requests
import time

ZIBAL_MERCHANT = os.environ.get("ZIBAL_MERCHANT", "zibal")

ZIBAL_BASE_URL = "https://gateway.zibal.ir"
ZIBAL_REQUEST_URL = f"{ZIBAL_BASE_URL}/v1/request"
ZIBAL_VERIFY_URL = f"{ZIBAL_BASE_URL}/v1/verify"
ZIBAL_STARTPAY = f"{ZIBAL_BASE_URL}/start/"


ZIBAL_RESULT_CODES = {
    100: "موفق",
    102: "merchant پیدا نشد",
    103: "merchant غیرفعال",
    104: "merchant نامعتبر",
    105: "amount نامعتبر",
    106: "callbackUrl نامعتبر",
    113: "amount نامعتبر",
    114: "mobile نامعتبر",
    115: "IP ثبت نشده",
    201: "قبلاً تأیید شده",
    202: "سفارش پرداخت نشده",
    203: "trackId نامعتبر",
}


def create_payment(amount, description, callback_url=None, mobile=None, order_id=None):
    if not ZIBAL_MERCHANT:
        return {"success": False, "error": "مرچنت تنظیم نشده", "code": -1}

    amount_rial = amount * 10

    if not callback_url:
        callback_url = "https://violexq.ir/payment/callback"

    payload = {
        "merchant": ZIBAL_MERCHANT,
        "amount": amount_rial,
        "description": description,
        "callbackUrl": callback_url,
    }

    if mobile:
        payload["mobile"] = mobile
    if order_id:
        payload["orderId"] = order_id

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        response = requests.post(ZIBAL_REQUEST_URL, json=payload, headers=headers, timeout=15)
        result = response.json()
        print(f"🟢 Zibal Request: {result}")

        if result.get("result") == 100:
            track_id = result.get("trackId")
            payment_url = f"{ZIBAL_STARTPAY}{track_id}"
            return {
                "success": True,
                "authority": str(track_id),
                "track_id": track_id,
                "payment_url": payment_url,
                "order_id": order_id,
            }
        else:
            code = result.get("result")
            error_msg = result.get("message", ZIBAL_RESULT_CODES.get(code, "خطای نامشخص"))
            return {"success": False, "error": error_msg, "code": code}
    except Exception as e:
        return {"success": False, "error": str(e)}


def verify_payment(track_id, amount):
    if not ZIBAL_MERCHANT:
        return {"success": False, "error": "مرچنت تنظیم نشده"}

    amount_rial = amount * 10

    payload = {
        "merchant": ZIBAL_MERCHANT,
        "amount": amount_rial,
        "trackId": int(track_id),
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        response = requests.post(ZIBAL_VERIFY_URL, json=payload, headers=headers, timeout=15)
        result = response.json()
        print(f"🟢 Zibal Verify: {result}")

        if result.get("result") == 100:
            return {
                "success": True,
                "ref_id": result.get("refNumber", "-"),
                "card_pan": result.get("cardNumber", "-"),
            }
        elif result.get("result") == 201:
            return {
                "success": True,
                "already_verified": True,
                "ref_id": result.get("refNumber", "-"),
                "card_pan": result.get("cardNumber", "-"),
            }
        else:
            code = result.get("result")
            error_msg = result.get("message", ZIBAL_RESULT_CODES.get(code, "خطای تأیید"))
            return {"success": False, "error": error_msg, "code": code}
    except Exception as e:
        return {"success": False, "error": str(e)}