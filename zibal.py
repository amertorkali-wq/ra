import os
import time
import requests
from config import ZIBAL_SANDBOX, ZIBAL_MERCHANT, ZIBAL_CALLBACK_URL

ZIBAL_BASE_URL = "https://gateway.zibal.ir"
ZIBAL_REQUEST_URL = f"{ZIBAL_BASE_URL}/v1/request"
ZIBAL_VERIFY_URL = f"{ZIBAL_BASE_URL}/v1/verify"
ZIBAL_INQUIRY_URL = f"{ZIBAL_BASE_URL}/v1/inquiry"
ZIBAL_STARTPAY = f"{ZIBAL_BASE_URL}/start/"

ZIBAL_RESULT_CODES = {
    100: "موفق",
    102: "merchant پیدا نشد",
    103: "merchant غیرفعال",
    104: "merchant نامعتبر",
    105: "amount باید بین 1000 تا 500000000 ریال باشد",
    106: "callbackUrl نامعتبر است",
    113: "amount نامعتبر است",
    114: "mobile نامعتبر است",
    115: "IP ثبت نشده است",
    201: "قبلاً تأیید شده",
    202: "سفارش پرداخت نشده یا ناموفق بوده",
    203: "trackId نامعتبر است",
}


def get_merchant() -> str:
    """در حالت sandbox از zibal استفاده می‌کند"""
    if ZIBAL_SANDBOX:
        return "zibal"
    return ZIBAL_MERCHANT


def create_payment(amount_toman: int, description: str,
                   callback_url: str = None, mobile: str = None,
                   order_id: str = None) -> dict:
    """
    درخواست پرداخت از زیبال

    Args:
        amount_toman: مبلغ به تومان
        description: توضیحات
        callback_url: آدرس بازگشت (پیش‌فرض از config)
        mobile: شماره موبایل
        order_id: شناسه سفارش

    Returns:
        dict: {'success': bool, 'authority': str, 'track_id': int, 'payment_url': str, ...}
    """
    merchant = get_merchant()
    if not merchant:
        return {"success": False, "error": "مرچنت تنظیم نشده", "code": -1}

    amount_rial = amount_toman * 10

    if not callback_url:
        callback_url = ZIBAL_CALLBACK_URL

    payload = {
        "merchant": merchant,
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
            print(f"🔴 Zibal Error Code: {code}, Message: {error_msg}")
            return {"success": False, "error": error_msg, "code": code}
    except Exception as e:
        print(f"🔴 Zibal Error: {e}")
        return {"success": False, "error": str(e)}


def verify_payment(track_id: int, amount_toman: int = None) -> dict:
    """
    تأیید پرداخت زیبال

    Args:
        track_id: شناسه تراکنش زیبال
        amount_toman: مبلغ مورد انتظار (به تومان) برای بررسی

    Returns:
        dict: {'success': bool, 'ref_id': str, 'card_pan': str, 'amount': int, ...}
    """
    merchant = get_merchant()
    if not merchant:
        return {"success": False, "error": "مرچنت تنظیم نشده"}

    payload = {
        "merchant": merchant,
        "trackId": int(track_id),
    }

    if amount_toman is not None:
        payload["amount"] = amount_toman * 10  # بررسی مبلغ

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
                "amount_rial": result.get("amount", 0),
                "amount_toman": result.get("amount", 0) // 10,
            }
        elif result.get("result") == 201:
            return {
                "success": True,
                "already_verified": True,
                "ref_id": result.get("refNumber", "-"),
                "card_pan": result.get("cardNumber", "-"),
                "amount_rial": result.get("amount", 0),
                "amount_toman": result.get("amount", 0) // 10,
            }
        else:
            code = result.get("result")
            error_msg = result.get("message", ZIBAL_RESULT_CODES.get(code, "خطای تأیید"))
            print(f"🔴 Zibal Verify Error: {code} - {error_msg}")
            return {"success": False, "error": error_msg, "code": code}
    except Exception as e:
        print(f"🔴 Zibal Verify Error: {e}")
        return {"success": False, "error": str(e)}


def inquiry_payment(track_id: int) -> dict:
    """استعلام تراکنش از زیبال"""
    merchant = get_merchant()
    if not merchant:
        return {"success": False, "error": "مرچنت تنظیم نشده"}

    payload = {"merchant": merchant, "trackId": int(track_id)}
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    try:
        response = requests.post(ZIBAL_INQUIRY_URL, json=payload, headers=headers, timeout=15)
        return response.json()
    except Exception as e:
        print(f"🔴 Zibal Inquiry Error: {e}")
        return {"success": False, "error": str(e)}