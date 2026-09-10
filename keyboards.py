"""
اتصال به درگاه پرداخت زرین‌پال
"""
import requests
from config import ZARINPAL_MERCHANT, ZARINPAL_SANDBOX


if ZARINPAL_SANDBOX:
    ZARINPAL_REQUEST_URL = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
    ZARINPAL_VERIFY_URL = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
    ZARINPAL_STARTPAY = "https://sandbox.zarinpal.com/pg/StartPay/"
else:
    ZARINPAL_REQUEST_URL = "https://payment.zarinpal.com/pg/v4/payment/request.json"
    ZARINPAL_VERIFY_URL = "https://payment.zarinpal.com/pg/v4/payment/verify.json"
    ZARINPAL_STARTPAY = "https://payment.zarinpal.com/pg/StartPay/"


def create_payment(amount, description, callback_url=None, mobile=None, email=None):
    """ایجاد تراکنش در زرین‌پال"""
    amount_rial = amount * 10

    payload = {
        "merchant_id": ZARINPAL_MERCHANT,
        "amount": amount_rial,
        "description": description,
        "callback_url": callback_url or "https://t.me/VIOLEXQ_bot",
    }

    if mobile:
        payload["metadata"] = {"mobile": mobile}
    if email:
        payload["metadata"] = payload.get("metadata", {})
        payload["metadata"]["email"] = email

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        response = requests.post(
            ZARINPAL_REQUEST_URL,
            json=payload,
            headers=headers,
            timeout=15
        )
        result = response.json()
        print(f"🟢 Zarinpal Request: {result}")

        if result.get("data") and result["data"].get("code") == 100:
            authority = result["data"]["authority"]
            payment_url = f"{ZARINPAL_STARTPAY}{authority}"
            return {
                "success": True,
                "authority": authority,
                "payment_url": payment_url,
                "fee": result["data"].get("fee", 0),
            }
        else:
            error = result.get("errors", {})
            return {
                "success": False,
                "error": str(error),
                "code": error.get("code") if isinstance(error, dict) else None,
            }
    except Exception as e:
        print(f"🔴 Zarinpal Error: {e}")
        return {"success": False, "error": str(e)}


def verify_payment(authority, amount):
    """تأیید تراکنش"""
    amount_rial = amount * 10

    payload = {
        "merchant_id": ZARINPAL_MERCHANT,
        "amount": amount_rial,
        "authority": authority,
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        response = requests.post(
            ZARINPAL_VERIFY_URL,
            json=payload,
            headers=headers,
            timeout=15
        )
        result = response.json()
        print(f"🟢 Zarinpal Verify: {result}")

        if result.get("data") and result["data"].get("code") == 100:
            return {
                "success": True,
                "ref_id": result["data"].get("ref_id"),
                "card_pan": result["data"].get("card_pan", ""),
                "card_hash": result["data"].get("card_hash", ""),
            }
        elif result.get("data") and result["data"].get("code") == 101:
            return {
                "success": True,
                "ref_id": result["data"].get("ref_id"),
                "already_verified": True,
            }
        else:
            error = result.get("errors", {})
            return {
                "success": False,
                "error": str(error),
                "code": error.get("code") if isinstance(error, dict) else None,
            }
    except Exception as e:
        print(f"🔴 Zarinpal Verify Error: {e}")
        return {"success": False, "error": str(e)}