"""
وب‌سرور callback زیبال
این سرور روی همون پروسه ربات اجرا می‌شه و callback رو دریافت می‌کنه
"""
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import html

from config import WEB_PORT, RAILWAY_PUBLIC_DOMAIN, DEFAULT_PACKAGES, TRANSACTION_CHANNEL
from database import (
    get_payment_by_authority_full,
    update_payment_status,
    update_user,
    add_transaction,
    get_shamsi_now,
    get_user,
    get_shamsi_future_date,
)
from zibal import verify_payment


# برای دسترسی به bot instance از اینجا
_bot_instance = None


def set_bot_instance(bot):
    global _bot_instance
    _bot_instance = bot


class CallbackHandler(BaseHTTPRequestHandler):
    """هندلر callback زیبال"""

    def log_message(self, format, *args):
        print(f"🌐 [HTTP] {self.address_string()} - {format % args}")

    def do_GET(self):
        parsed = urlparse(self.path)

        # ---- مسیر /zibal/callback ----
        if parsed.path == "/zibal/callback":
            self.handle_zibal_callback(parsed)
            return

        # ---- مسیر / ----
        if parsed.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                "<html><body style='font-family:Tahoma;text-align:center;padding:50px;'>"
                "<h1>✅ VIOLEX Payment Server</h1>"
                "<p>سرور پرداخت در حال اجراست.</p>"
                "</body></html>".encode("utf-8")
            )
            return

        # ---- مسیر /health ----
        if parsed.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def handle_zibal_callback(self, parsed):
        """پردازش callback زیبال"""
        params = parse_qs(parsed.query)

        track_id = params.get("trackId", [None])[0]
        success_param = params.get("success", [None])[0]
        status_param = params.get("status", [None])[0]
        order_id = params.get("orderId", [None])[0]

        print(f"\n🔵 [ZIBAL CALLBACK] trackId={track_id} success={success_param} status={status_param}")

        # ---- اعتبارسنجی اولیه ----
        if not track_id:
            print("🔴 No trackId in callback")
            self.send_result_page("نامعتبر", "پارامتر trackId دریافت نشد.")
            return

        # ---- بررسی وجود پرداخت در دیتابیس ----
        payment = get_payment_by_authority_full(track_id)

        if not payment:
            print(f"🔴 Payment not found: {track_id}")
            self.send_result_page("نامعتبر", "این تراکنش در سیستم ثبت نشده است.")
            return

        # ---- بررسی double-spend ----
        if payment['status'] == 'verified':
            print(f"⚠️ Payment already verified: {track_id}")
            self.send_result_page(
                "قبلاً تأیید شده",
                "این تراکنش قبلاً تأیید شده و پکیج فعال شده است."
            )
            return

        if payment['status'] == 'failed':
            print(f"⚠️ Payment already failed: {track_id}")
            self.send_result_page("ناموفق", "این تراکنش قبلاً ناموفق ثبت شده است.")
            return

        # ---- بررسی موفقیت از سمت زیبال ----
        if success_param != "1" or status_param != "2":
            print(f"🔴 Payment unsuccessful: success={success_param} status={status_param}")
            update_payment_status(track_id, 'failed')
            self.send_result_page(
                "ناموفق",
                "پرداخت توسط شما لغو شد یا ناموفق بود."
            )
            return

        # ---- Verify با API زیبال ----
        print(f"🟢 Verifying payment {track_id}...")
        verify_result = verify_payment(int(track_id), amount_toman=payment['amount'])

        if not verify_result.get('success'):
            error = verify_result.get('error', 'خطای نامشخص')
            print(f"🔴 Verify failed: {error}")
            update_payment_status(track_id, 'failed')
            self.send_result_page(
                "تأیید ناموفق",
                f"تأیید پرداخت با خطا مواجه شد: {error}"
            )
            return

        # ---- بررسی مبلغ ----
        paid_amount_rial = verify_result.get('amount_rial', 0)
        expected_amount_rial = payment['amount'] * 10

        if paid_amount_rial != expected_amount_rial:
            print(f"🔴 Amount mismatch! paid={paid_amount_rial} expected={expected_amount_rial}")
            update_payment_status(track_id, 'failed')
            self.send_result_page(
                "خطا",
                "مبلغ پرداخت‌شده با مبلغ ثبت‌شده مطابقت ندارد."
            )
            return

        # ---- موفق! فعال‌سازی پکیج ----
        print(f"✅ Payment verified successfully! trackId={track_id}")

        ref_id = verify_result.get('ref_id', '-')
        card_pan = verify_result.get('card_pan', '-')

        # آپدیت پرداخت
        update_payment_status(track_id, 'verified', ref_id, card_pan)

        # ثبت تراکنش
        add_transaction(
            payment['user_id'],
            payment['amount'],
            card_pan,
            ref_id,
            "success",
            "package"
        )

        # فعال‌سازی پکیج
        user_id = payment['user_id']
        package_id = payment['package_id']

        if package_id is not None:
            pkg = next((p for p in DEFAULT_PACKAGES if p['id'] == package_id), None)
            if pkg:
                user = get_user(user_id)
                if user:
                    current_questions = user[8] or 0
                    new_questions = current_questions + pkg['questions']
                    expire_date = get_shamsi_future_date(pkg['days'])

                    update_user(
                        user_id,
                        questions_remaining=new_questions,
                        active_package=pkg['name'],
                        package_expire_date=expire_date,
                    )

                    print(f"✅ Package '{pkg['name']}' activated for user {user_id}")

                    # ارسال پیام به کاربر
                    if _bot_instance:
                        try:
                            loop = _bot_instance.loop
                            if loop and loop.is_running():
                                asyncio.run_coroutine_threadsafe(
                                    send_success_message(
                                        user_id, pkg, ref_id, card_pan,
                                        new_questions, expire_date,
                                    ),
                                    loop,
                                )
                        except Exception as e:
                            print(f"🔴 Error sending message: {e}")

                    # گزارش به کانال
                    if _bot_instance:
                        try:
                            loop = _bot_instance.loop
                            if loop and loop.is_running():
                                asyncio.run_coroutine_threadsafe(
                                    send_channel_report(
                                        user_id, pkg, ref_id, card_pan, payment['amount'],
                                    ),
                                    loop,
                                )
                        except Exception as e:
                            print(f"🔴 Error sending channel report: {e}")

        # ---- نمایش صفحه موفقیت ----
        self.send_result_page(
            "موفق",
            "پرداخت شما با موفقیت انجام شد. لطفاً به ربات برگردید و روی «پرداخت کردم» بزنید.",
            success=True,
        )

    def send_result_page(self, title, message, success=False):
        """ارسال صفحه نتیجه HTML"""
        color = "#4CAF50" if success else "#f44336"
        icon = "✅" if success else "❌"

        html_content = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)} - ویولکس</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: Tahoma, sans-serif;
            text-align: center;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        .box {{
            background: white;
            padding: 50px 40px;
            border-radius: 24px;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        .icon {{ font-size: 80px; margin-bottom: 20px; }}
        h1 {{ color: {color}; font-size: 28px; margin-bottom: 15px; }}
        p {{ color: #666; font-size: 16px; line-height: 1.8; margin-bottom: 30px; }}
        a {{
            display: inline-block;
            padding: 16px 45px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 12px;
            font-weight: bold;
            font-size: 16px;
        }}
    </style>
</head>
<body>
    <div class="box">
        <div class="icon">{icon}</div>
        <h1>{html.escape(title)}</h1>
        <p>{html.escape(message)}</p>
        <a href="https://t.me/VIOLEXQ_bot">🔙 بازگشت به ربات</a>
    </div>
</body>
</html>"""

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html_content.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))


async def send_success_message(user_id, pkg, ref_id, card_pan, new_questions, expire_date):
    """ارسال پیام موفقیت به کاربر"""
    if not _bot_instance:
        return
    try:
        await _bot_instance.send_message(
            chat_id=user_id,
            text=(
                f"✅ *پرداخت شما با موفقیت انجام شد!*\n\n"
                f"📦 پکیج: {pkg['name']}\n"
                f"❓ تعداد سوال: {pkg['questions']}\n"
                f"⏳ اعتبار تا: {expire_date}\n"
                f"📚 مجموع سوالات باقی‌مانده: {new_questions}\n\n"
                f"🆔 کد پیگیری: `{ref_id}`\n"
                f"💳 کارت: `{card_pan}`\n\n"
                f"🌟 از اینکه ویولکس را انتخاب کردید سپاسگزاریم."
            ),
            parse_mode="Markdown",
        )
    except Exception as e:
        print(f"🔴 send_success_message error: {e}")


async def send_channel_report(user_id, pkg, ref_id, card_pan, amount):
    """ارسال گزارش به کانال تراکنش"""
    if not _bot_instance:
        return
    try:
        await _bot_instance.send_message(
            chat_id=TRANSACTION_CHANNEL,
            text=(
                f"📢 *گزارش تراکنش*\n\n"
                f"👤 کاربر: `{user_id}`\n"
                f"💰 مبلغ: {amount:,} تومان\n"
                f"🎁 پکیج: {pkg['name']}\n"
                f"🆔 کد پیگیری: `{ref_id}`\n"
                f"💳 کارت: `{card_pan}`\n"
                f"🕐 زمان: {get_shamsi_now()}"
            ),
            parse_mode="Markdown",
        )
    except Exception as e:
        print(f"🔴 send_channel_report error: {e}")


def run_server():
    """اجرای وب‌سرور در thread جداگانه"""
    server = HTTPServer(("0.0.0.0", WEB_PORT), CallbackHandler)
    print(f"🌐 Payment server running on port {WEB_PORT}")
    print(f"🔗 Callback URL: https://{RAILWAY_PUBLIC_DOMAIN}/zibal/callback")
    server.serve_forever()


def start_payment_server():
    """شروع وب‌سرور در thread جداگانه"""
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    return thread