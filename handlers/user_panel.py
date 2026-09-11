import random
import requests
from datetime import datetime
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
)
from telegram.ext import ContextTypes

from config import (
    CHANNEL_ID, BOT_LINK, DEFAULT_PACKAGES,
    SUBJECTS, ABOUT_IMAGE_URL, ACCOUNTING_GROUP, SUPPORT_GROUP,
    SMSIR_API_KEY, SMSIR_TEMPLATE_ID, SMSIR_LINE_NUMBER,
    TRANSACTION_CHANNEL
)
from database import (
    get_user, create_user, update_user, get_user_cards, get_verified_cards,
    add_card, delete_card, create_question, create_ticket, add_transaction,
    reward_inviter, get_shamsi_now, get_shamsi_future_date,
    set_verification_code, get_verification_code,
    create_payment_record, update_payment_status,
    get_user_open_ticket, get_card,
    get_discount_code, use_discount_code,
    get_user_referral_stats,
)
from zibal import create_payment, verify_payment
from keyboards import (
    get_force_buttons, get_main_menu_keyboard, get_lesson_keyboard,
    get_balance_buttons, get_auth_buttons, get_about_buttons,
    get_packages_buttons, get_start_package_activated_buttons,
    get_cards_for_payment, get_invoice_buttons,
    get_back_keyboard, get_cancel_question_keyboard, get_phone_share_keyboard,
    get_payment_buttons, get_user_ticket_buttons, get_cancel_ticket_keyboard,
    get_cards_delete_buttons, get_delete_confirm_buttons
)
from texts import (
    FORCE_MSG, NOT_MEMBER_MSG, WELCOME_MSG, MAIN_MENU_TEXT,
    INCREASE_BALANCE_TEXT, AUTH_TEXT, ABOUT_US_TEXT,
    PACKAGES_TEXT, PACKAGES_TEXT_WITH_START, START_PACKAGE_ACTIVATED,
    BUY_QUESTION_TEXT, NO_PACKAGE_MSG, NO_QUESTION_MSG, SUPPORT_TEXT,
    INVITE_TEXT_1, INVITE_TEXT_2, RULES_TEXT, HELP_TEXT,
    CARD_NUMBER_REQUEST, CARD_PHOTO_REQUEST, CARD_REGISTERED,
    AUTH_PHONE_SHARE, AUTH_RULES_CONFIRM, AUTH_PHONE_VERIFIED,
    RULES_FOR_AUTH_TEXT, FOREIGN_PHONE_ERROR,
    SUPPORT_TICKET_CREATED, SUPPORT_HAS_OPEN_TICKET,
    get_account_text, get_invoice_text,
    PAYMENT_SUCCESS, PAYMENT_PENDING, PAYMENT_VERIFY_FAILED
)


# ============================================
# ارسال پیامک
# ============================================

def send_verification_sms(phone_number, code):
    url = "https://api.sms.ir/v1/send/verify"
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/plain",
        "x-api-key": SMSIR_API_KEY,
    }
    payload = {
        "mobile": phone_number,
        "templateId": SMSIR_TEMPLATE_ID,
        "parameters": [
            {"name": "VERIFICATIONCODE", "value": str(code)},
            {"name": "TIME", "value": "5"}
        ]
    }
    print(f"🔵 SMS Request: mobile={phone_number}")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        result = response.json()
        print(f"🟢 SMS.ir Response: {result}")
        return result.get("status") == 1
    except Exception as e:
        print(f"🔴 SMS Error: {e}")
        return False


async def is_user_member(application, user_id: int) -> bool:
    try:
        member = await application.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False


def get_user_info(user_id):
    user = get_user(user_id)
    if not user:
        return None
    return {
        'user_id': user[0],
        'username': user[1],
        'first_name': user[2],
        'last_name': user[3],
        'phone': user[4],
        'phone_verified': user[5],
        'verification_code': user[6],
        'wallet': user[7],
        'questions_remaining': user[8],
        'questions_used': user[9],
        'active_package': user[10],
        'package_expire_date': user[11],
        'referrals': user[12],
        'invited_by': user[13],
        'invited_by_rewarded': user[14],
        'has_start_package': user[15],
        'is_blocked': user[16],
        'role': user[17],
    }


def clear_user_states(context):
    states = [
        'awaiting_auth_phone', 'awaiting_auth_code',
        'awaiting_card_photo', 'awaiting_card_number',
        'awaiting_question', 'awaiting_description',
        'awaiting_question_count', 'awaiting_support',
        'awaiting_support_message', 'support_message',
        'awaiting_discount_code', 'discount_invoice_id',
        'in_ticket', 'card_photo', 'selected_subject',
        'question_text', 'question_file', 'selected_package',
        'selected_card_id', 'payment_authority', 'payment_amount',
        'remaining_amount', 'question_purchase', 'question_purchase_amount',
        'invoice_id', 'card_number_temp',
    ]
    for state in states:
        context.user_data.pop(state, None)


# ============================================
# /start
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    clear_user_states(context)

    invited_by = None
    if context.args and len(context.args) > 0:
        try:
            invited_by = int(context.args[0])
            if invited_by == user_id:
                invited_by = None
        except:
            pass

    is_new = not get_user(user_id)
    if is_new:
        create_user(user_id, user.username, user.first_name, user.last_name, invited_by)

    if await is_user_member(context.application, user_id):
        # ⚠️ پاداش اینجا داده نمی‌شه! فقط بعد از احراز هویت کامل
        await update.message.reply_text(
            WELCOME_MSG,
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            FORCE_MSG,
            reply_markup=get_force_buttons(),
            disable_web_page_preview=True,
        )


async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    message = query.message

    if await is_user_member(context.application, user_id):
        # ⚠️ پاداش اینجا داده نمی‌شه!
        try:
            await message.delete()
        except:
            pass
        await query.message.reply_text(
            WELCOME_MSG,
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await query.edit_message_text(
            NOT_MEMBER_MSG,
            reply_markup=get_force_buttons(),
            disable_web_page_preview=True,
        )


# ============================================
# دکمه‌های افزایش موجودی
# ============================================

async def handle_balance_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    user_info = get_user_info(user_id)

    # ---- احراز هویت ----
    if data == "auth":
        try:
            await query.edit_message_text(
                AUTH_TEXT,
                reply_markup=get_auth_buttons(),
                parse_mode="Markdown"
            )
        except:
            pass

    # ---- خرید پکیج ----
    elif data == "buy_package":
        cards = get_verified_cards(user_id)
        all_cards = get_user_cards(user_id)

        if not cards:
            pending_cards = [c for c in all_cards if not c[5]]

            if pending_cards:
                text = (
                    "⏳ *شما کارت در انتظار تأیید دارید.*\n\n"
                    "کارت شما هنوز توسط حسابدار تأیید نشده است.\n"
                    "لطفاً تا تأیید کارت صبر کنید.\n\n"
                    "💡 پس از تأیید، به شما اطلاع داده می‌شود."
                )
            else:
                text = (
                    "❗ *شما هنوز کارت بانکی تأیید شده‌ای ندارید.*\n\n"
                    "لطفاً از بخش «احراز هویت» اقدام کنید."
                )

            try:
                await query.edit_message_text(
                    text,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🪪 احراز هویت", callback_data="auth", style="primary")],
                        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_balance", style="danger")],
                    ]),
                    parse_mode="Markdown"
                )
            except:
                pass
        else:
            has_start = user_info['has_start_package'] == 1
            text = PACKAGES_TEXT if has_start else PACKAGES_TEXT_WITH_START
            try:
                await query.edit_message_text(
                    text,
                    reply_markup=get_packages_buttons(has_start_package=has_start),
                    parse_mode="Markdown"
                )
            except:
                pass

    # ---- بازگشت به پکیج‌ها ----
    elif data == "back_to_packages":
        has_start = user_info['has_start_package'] == 1
        text = PACKAGES_TEXT if has_start else PACKAGES_TEXT_WITH_START
        try:
            await query.edit_message_text(
                text,
                reply_markup=get_packages_buttons(has_start_package=has_start),
                parse_mode="Markdown"
            )
        except:
            pass

    # ---- خرید سوال ----
    elif data == "buy_question":
        try:
            await query.edit_message_text(
                BUY_QUESTION_TEXT,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 برگشت", callback_data="back_to_balance", style="danger")]
                ])
            )
        except:
            pass
        context.user_data['awaiting_question_count'] = True

    # ---- بازگشت به منوی اصلی ----
    elif data == "back_to_main":
        clear_user_states(context)
        try:
            await query.message.delete()
        except:
            pass
        await query.message.reply_text(
            MAIN_MENU_TEXT,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )

    # ---- بازگشت به افزایش موجودی ----
    elif data == "back_to_balance":
        try:
            await query.edit_message_text(
                INCREASE_BALANCE_TEXT,
                reply_markup=get_balance_buttons()
            )
        except:
            pass

    # ---- انتخاب پکیج ----
    elif data.startswith("buy_pkg_"):
        pkg_id = int(data.split("_")[2])
        pkg = next((p for p in DEFAULT_PACKAGES if p['id'] == pkg_id), None)
        if not pkg:
            return

        # پکیج استارت
        if pkg['is_start']:
            if user_info['has_start_package']:
                try:
                    await query.edit_message_text(
                        "⚠️ شما قبلاً پکیج استارت را استفاده کرده‌اید.",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("🔙 برگشت", callback_data="back_to_balance", style="danger")]
                        ])
                    )
                except:
                    pass
                return

            expire_date = get_shamsi_future_date(pkg['days'])
            update_user(
                user_id,
                active_package=pkg['name'],
                package_expire_date=expire_date,
                questions_remaining=user_info['questions_remaining'] + pkg['questions'],
                has_start_package=1
            )
            try:
                await query.edit_message_text(
                    START_PACKAGE_ACTIVATED.format(
                        name=pkg['name'],
                        questions=pkg['questions'],
                        expire_date=expire_date
                    ),
                    reply_markup=get_start_package_activated_buttons(),
                    parse_mode="Markdown"
                )
            except:
                pass
            return

        # پکیج عادی
        cards = get_verified_cards(user_id)
        if not cards:
            try:
                await query.edit_message_text(
                    "❗ شما کارت تأیید شده ندارید. ابتدا احراز هویت کنید.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🪪 احراز هویت", callback_data="auth", style="primary")]
                    ])
                )
            except:
                pass
            return

        context.user_data['selected_package'] = pkg

        try:
            await query.edit_message_text(
                f"💳 *لطفاً کارت بانکی که قصد پرداخت با آن را دارید انتخاب کنید.*\n\n"
                f"📦 پکیج انتخابی: {pkg['name']}\n"
                f"💰 مبلغ: {pkg['price']:,} تومان\n"
                f"❓ تعداد سوال: {pkg['questions']}",
                reply_markup=get_cards_for_payment(cards),
                parse_mode="Markdown"
            )
        except:
            pass

    # ---- انتخاب کارت برای پرداخت ----
    elif data.startswith("pay_card_"):
        card_id = int(data.split("_")[2])
        pkg = context.user_data.get('selected_package')
        if not pkg:
            return

        wallet = user_info['wallet']
        total_price = pkg['price']
        context.user_data['selected_card_id'] = card_id

        import time
        invoice_id = int(time.time())
        context.user_data['invoice_id'] = invoice_id

        wallet_deduction = min(wallet, total_price)
        remaining = total_price - wallet_deduction

        invoice_text = (
            f"*📜 پیش فاکتور شماره:* `{invoice_id}`\n"
            f"*📦 خدمات:* خرید پکیج\n"
            f"*🖌️ نام پکیج:* {pkg['name']}\n"
            f"*💰 قیمت:* {total_price * 10:,}ریال\n"
            f"*💰 کسر از کیف پول:* {wallet_deduction * 10:,}ریال\n"
            f"*💰 قابل پرداخت:* {remaining * 10:,}ریال\n"
            f"*⏰ اعتبار زمانی:* {pkg['days']}روز\n"
            f"*❓ تعداد سوال:* {pkg['questions']}عدد\n"
        )

        if remaining > 0:
            description = f"خرید {pkg['name']} - ویولکس"
            result = create_payment(
                amount=remaining,
                description=description,
                mobile=user_info.get('phone'),
            )

            if result.get('success'):
                authority = result['authority']
                payment_url = result['payment_url']
                create_payment_record(user_id, authority, remaining, description, card_id)

                context.user_data['payment_authority'] = authority
                context.user_data['payment_amount'] = remaining

                invoice_text += (
                    f"*🔗 در لینک زیر پرداخت خود را انجام دهید*\n"
                    f"{payment_url}"
                )

                try:
                    await query.edit_message_text(
                        invoice_text,
                        reply_markup=get_invoice_buttons(invoice_id),
                        parse_mode="Markdown",
                        disable_web_page_preview=True
                    )
                except:
                    pass
            else:
                try:
                    await query.edit_message_text(
                        f"❌ خطا در ایجاد تراکنش.\n\n"
                        f"خطا: {result.get('error', 'نامشخص')}",
                    )
                except:
                    pass
        else:
            invoice_text += f"*✅ مبلغ قابل پرداخت: 0ریال (کیف پول کافی است)*"
            context.user_data['payment_amount'] = 0
            context.user_data['payment_authority'] = "wallet"

            try:
                await query.edit_message_text(
                    invoice_text,
                    reply_markup=get_invoice_buttons(invoice_id),
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
            except:
                pass

    # ---- پرداخت کردم ----
    elif data.startswith("paid_check_"):
        authority = context.user_data.get('payment_authority')
        amount = context.user_data.get('payment_amount')
        pkg = context.user_data.get('selected_package')

        if not pkg:
            await query.answer("⚠️ اطلاعات پکیج یافت نشد.", show_alert=True)
            return

        # پرداخت با کیف پول
        if authority == "wallet" or amount == 0:
            new_wallet = user_info['wallet'] - pkg['price']
            new_questions = user_info['questions_remaining'] + pkg['questions']
            expire_date = get_shamsi_future_date(pkg['days'])

            update_user(
                user_id,
                wallet=max(0, new_wallet),
                questions_remaining=new_questions,
                active_package=pkg['name'],
                package_expire_date=expire_date
            )
            add_transaction(user_id, pkg['price'], "wallet", "-", "success", "package")

            try:
                await query.edit_message_text(
                    f"✅ پرداخت با کیف پول انجام شد.\n\n"
                    f"📦 پکیج: {pkg['name']}\n"
                    f"❓ تعداد سوال: {pkg['questions']}\n"
                    f"⏳ اعتبار تا: {expire_date}"
                )
            except:
                pass

            clear_user_states(context)
            return

        if not authority or amount is None:
            await query.answer("⚠️ اطلاعات پرداخت یافت نشد.", show_alert=True)
            return

        try:
            await query.edit_message_text("⏳ در حال بررسی پرداخت...")
        except:
            pass

        result = verify_payment(authority, amount)

        if result.get('success'):
            ref_id = result.get('ref_id', '-')
            card_pan = result.get('card_pan', '-')
            update_payment_status(authority, 'verified', ref_id, card_pan)

            new_wallet = user_info['wallet'] - min(user_info['wallet'], pkg['price'])
            new_questions = user_info['questions_remaining'] + pkg['questions']
            expire_date = get_shamsi_future_date(pkg['days'])
            update_user(
                user_id,
                wallet=new_wallet,
                questions_remaining=new_questions,
                active_package=pkg['name'],
                package_expire_date=expire_date
            )
            add_transaction(user_id, amount, card_pan, ref_id, "success", "package")

            try:
                await query.edit_message_text(
                    f"✅ پرداخت شما با موفقیت انجام شد!\n\n"
                    f"📦 پکیج: {pkg['name']}\n"
                    f"🆔 کد پیگیری: {ref_id}\n"
                    f"💳 کارت: {card_pan}\n\n"
                    f"از اینکه ویولکس را انتخاب کردید سپاسگزاریم 🌟"
                )
            except:
                pass

            try:
                await context.bot.send_message(
                    chat_id=TRANSACTION_CHANNEL,
                    text=(
                        f"📢 گزارش تراکنش\n\n"
                        f"👤 کاربر: @{query.from_user.username or 'ندارد'}\n"
                        f"🆔 ID: {user_id}\n"
                        f"💰 مبلغ: {amount:,} تومان\n"
                        f"🎁 پکیج: {pkg['name']}\n"
                        f"🆔 کد پیگیری: {ref_id}\n"
                        f"💳 کارت: {card_pan}\n"
                        f"🕐 زمان: {get_shamsi_now()}"
                    )
                )
            except:
                pass

            clear_user_states(context)
        else:
            error_code = result.get('code')
            if error_code == 101:
                try:
                    await query.edit_message_text("✅ پرداخت شما قبلاً تأیید شده است.")
                except:
                    pass
            else:
                try:
                    await query.edit_message_text(
                        f"⚠️ تأیید پرداخت ناموفق بود.\n\n"
                        f"اگر مبلغی از حساب شما کسر شده، لطفاً با پشتیبانی تماس بگیرید.\n\n"
                        f"🆔 کد پیگیری: {authority}"
                    )
                except:
                    pass

    # ---- کد تخفیف ----
    elif data.startswith("discount_"):
        invoice_id = int(data.split("_")[1])
        context.user_data['awaiting_discount_code'] = True
        context.user_data['discount_invoice_id'] = invoice_id

        await query.message.reply_text(
            "🎁 لطفاً کد تخفیف خود را وارد کنید:"
        )


# ============================================
# دکمه‌های احراز هویت
# ============================================

async def handle_auth_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    user_info = get_user_info(user_id)

    # ---- لیست کارت‌ها ----
    if data == "card_list":
        cards = get_user_cards(user_id)
        if cards:
            text = "🧾 *لیست کارت‌های شما:*\n\n"
            for i, card in enumerate(cards):
                masked = f"{card[2][:4]} **** **** {card[2][-4:]}"
                status = "✅ تأیید شده" if card[5] else "⏳ در انتظار تأیید"
                star = "⭐ " if card[6] else ""
                text += f"{i+1}️⃣ {star}`{masked}`\n   وضعیت: {status}\n\n"
        else:
            text = "🧾 *شما هیچ کارتی ثبت نکرده‌اید.*"
        try:
            await query.edit_message_text(text, reply_markup=get_auth_buttons(), parse_mode="Markdown")
        except:
            pass

    # ---- افزودن کارت ----
    elif data == "add_card":
        if not user_info['phone_verified']:
            try:
                await query.edit_message_text(
                    RULES_FOR_AUTH_TEXT,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 بازگشت به احراز هویت", callback_data="auth", style="danger")]
                    ]),
                    parse_mode="Markdown"
                )
            except:
                pass
            await query.message.reply_text(
                AUTH_PHONE_SHARE,
                reply_markup=get_phone_share_keyboard(),
                parse_mode="Markdown"
            )
            context.user_data['awaiting_auth_phone'] = True
        else:
            context.user_data['awaiting_card_number'] = True
            try:
                await query.edit_message_text(
                    "➕ برای افزودن کارت، *شماره کارت* خود را وارد کنید.\n"
                    "فقط کارت‌هایی که به نام شما هستند قابل ثبت‌اند ⚠️",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 بازگشت به احراز هویت", callback_data="auth", style="danger")]
                    ]),
                    parse_mode="Markdown"
                )
            except:
                pass

    # ---- حذف کارت ----
    elif data == "remove_card":
        cards = get_user_cards(user_id)
        if not cards:
            try:
                await query.edit_message_text(
                    "⚠️ شما هیچ کارتی برای حذف ندارید.",
                    reply_markup=get_auth_buttons()
                )
            except:
                pass
        else:
            try:
                await query.edit_message_text(
                    "🗑 کارت مورد نظر برای حذف را انتخاب کنید:",
                    reply_markup=get_cards_delete_buttons(cards)
                )
            except:
                pass

    # ---- انتخاب کارت برای حذف ----
    elif data.startswith("del_card_"):
        card_id = int(data.split("_")[2])
        card = get_card(card_id)

        if not card:
            await query.answer("⚠️ کارت یافت نشد.", show_alert=True)
            return

        masked = f"{card[2][:4]} **** **** {card[2][-4:]}"

        try:
            await query.edit_message_text(
                f"*💳 شماره کارت {masked} دریافت شد.*\n"
                f"*اگر این کارت را می‌خواهید حذف کنید، روی دکمه «حذف» بزنید 🗑️*",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🗑 حذف", callback_data=f"confirm_del_card_{card_id}", style="danger")],
                    [InlineKeyboardButton("❌ انصراف", callback_data="card_list", style="primary")],
                ]),
                parse_mode="Markdown"
            )
        except:
            pass

    # ---- تایید حذف کارت ----
    elif data.startswith("confirm_del_card_"):
        card_id = int(data.split("_")[3])
        card = get_card(card_id)

        if not card:
            await query.answer("⚠️ کارت یافت نشد.", show_alert=True)
            return

        masked = f"{card[2][:4]} **** **** {card[2][-4:]}"
        delete_card(card_id)

        cards = get_user_cards(user_id)
        if cards:
            text = "🧾 *لیست کارت‌های شما:*\n\n"
            for i, c in enumerate(cards):
                m = f"{c[2][:4]} **** **** {c[2][-4:]}"
                status = "✅ تأیید شده" if c[5] else "⏳ در انتظار تأیید"
                star = "⭐ " if c[6] else ""
                text += f"{i+1}️⃣ {star}`{m}`\n   وضعیت: {status}\n\n"
        else:
            text = "🧾 *شما هیچ کارتی ثبت نکرده‌اید.*"

        try:
            await query.edit_message_text(
                f"🗑️ کارت {masked} با موفقیت حذف شد!\n\n{text}",
                reply_markup=get_auth_buttons(),
                parse_mode="Markdown"
            )
        except:
            pass

    # ---- بازگشت به احراز هویت ----
    elif data == "auth":
        try:
            await query.edit_message_text(
                AUTH_TEXT,
                reply_markup=get_auth_buttons(),
                parse_mode="Markdown"
            )
        except:
            pass

    # ---- بازگشت به افزایش موجودی ----
    elif data == "back_to_balance":
        try:
            await query.edit_message_text(
                INCREASE_BALANCE_TEXT,
                reply_markup=get_balance_buttons()
            )
        except:
            pass


# ============================================
# دریافت شماره
# ============================================

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    if not contact:
        return

    user_id = update.effective_user.id

    if not context.user_data.get('awaiting_auth_phone'):
        await update.message.reply_text(
            "⚠️ *لطفاً ابتدا از بخش «افزودن کارت» اقدام کنید.*",
            parse_mode="Markdown",
            reply_markup=get_main_menu_keyboard()
        )
        return

    phone = contact.phone_number
    if phone.startswith("+"):
        phone = phone[1:]
    if phone.startswith("98"):
        phone = "0" + phone[2:]

    if not phone.startswith("09") or len(phone) != 11:
        await update.message.reply_text(
            FOREIGN_PHONE_ERROR,
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data['awaiting_auth_phone'] = False
        return

    if contact.user_id and contact.user_id != user_id:
        await update.message.reply_text(
            "⚠️ *لطفاً فقط شماره خودتان را ارسال کنید.*",
            parse_mode="Markdown"
        )
        return

    update_user(user_id, phone=phone)
    code = str(random.randint(10000, 99999))
    set_verification_code(user_id, code)

    success = send_verification_sms(phone, code)
    context.user_data['awaiting_auth_phone'] = False
    context.user_data['awaiting_auth_code'] = True

    if success:
        await update.message.reply_text(
            AUTH_RULES_CONFIRM,
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await update.message.reply_text(
            f"⚠️ سرویس پیامک موقتاً در دسترس نیست.\n\n"
            f"📨 کد تأیید شما: `{code}`\n\n"
            f"👇 لطفاً این کد را در ربات وارد کنید.",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )


# ============================================
# هندلر عکس
# ============================================

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if context.user_data.get('in_ticket'):
        ticket_id = context.user_data.get('in_ticket')
        from handlers import support_panel
        await support_panel.user_send_ticket_message(update, context, ticket_id)
        return

    # عکس کارت
    if context.user_data.get('awaiting_card_photo'):
        card_photo = update.message.photo[-1].file_id
        card_number = context.user_data.get('card_number_temp')

        if not card_number:
            context.user_data['card_photo'] = card_photo
            context.user_data['awaiting_card_number'] = True
            context.user_data['awaiting_card_photo'] = False
            await update.message.reply_text(
                "📷 عکس دریافت شد.\n\n"
                "✍️ حالا لطفاً *شماره کارت ۱۶ رقمی* خود را وارد کنید.",
                parse_mode="Markdown"
            )
            return

        card_id = add_card(user_id, card_number, update.effective_user.first_name or "کاربر", card_photo)

        context.user_data['awaiting_card_photo'] = False
        context.user_data.pop('card_number_temp', None)

        await update.message.reply_text(
            "✅ کارت شما ثبت شد.\n"
            "⏳ کارت در انتظار تأیید قرار دارد.",
            reply_markup=get_main_menu_keyboard()
        )

        user_info = get_user_info(user_id)
        try:
            await context.bot.send_photo(
                chat_id=ACCOUNTING_GROUP,
                photo=card_photo,
                caption=(
                    f"📌 احراز کارت جدید\n\n"
                    f"👤 کاربر: @{update.effective_user.username or 'ندارد'}\n"
                    f"🆔 آیدی: {user_id}\n"
                    f"📱 شماره: {user_info.get('phone', 'نامشخص') if user_info else 'نامشخص'}\n"
                    f"💳 شماره کارت: {card_number}\n"
                    f"👤 نام: {update.effective_user.first_name or ''}"
                ),
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("✅ تأیید کارت", callback_data=f"acc_verify_{card_id}", style="success"),
                        InlineKeyboardButton("❌ رد کارت", callback_data=f"acc_reject_{card_id}", style="danger"),
                    ]
                ])
            )
        except Exception as e:
            print(f"Error sending to accounting: {e}")
        return

    # عکس سوال
    if context.user_data.get('awaiting_question'):
        context.user_data['awaiting_question'] = False
        context.user_data['question_file'] = update.message.photo[-1].file_id
        context.user_data['question_text'] = update.message.caption or '[عکس]'
        context.user_data['awaiting_description'] = True
        await update.message.reply_text(
            "✍️ لطفاً مشکل خود را توضیح دهید.",
            reply_markup=get_cancel_question_keyboard()
        )
        return


# ============================================
# هندلر پیام‌های متنی
# ============================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    user_id = user.id

    if not await is_user_member(context.application, user.id):
        await update.message.reply_text(
            "⛔ لطفاً ابتدا در کانال عضو شوید و سپس /start را بزنید.",
            reply_markup=get_force_buttons()
        )
        return

    main_menu_buttons = [
        "👤 حساب من",
        "🤝 دعوت دوستان",
        "📋 درباره ما",
        "☎️ پشتیبانی",
        "🆘 قوانین",
        "📖 راهنما",
        "📚 ارسال سوال",
        "💸 افزایش موجودی",
        "🔙 برگشت",
        "🏠 منوی اصلی",
        "❌ لغو سوال",
        "❌ لغو تیکت",
        "📫 ارسال تیکت"
    ]

    if text in main_menu_buttons:
        if text not in ["📫 ارسال تیکت", "❌ لغو تیکت"]:
            clear_user_states(context)

    user_info = get_user_info(user_id)

    if not user_info:
        if not get_user(user_id):
            create_user(user_id, user.username, user.first_name, user.last_name)
        user_info = get_user_info(user_id)

    update_user(
        user_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )

    if context.user_data.get('in_ticket'):
        ticket_id = context.user_data.get('in_ticket')
        from handlers import support_panel
        await support_panel.user_send_ticket_message(update, context, ticket_id)
        return

    # ---- کد تأیید ----
    if context.user_data.get('awaiting_auth_code'):
        entered_code = text.strip()
        stored_code = get_verification_code(user_id)

        if stored_code and entered_code == stored_code:
            context.user_data['awaiting_auth_code'] = False
            update_user(user_id, phone_verified=1)
            context.user_data['awaiting_card_number'] = True

            # ⚠️ پاداش به دعوت‌کننده بعد از احراز هویت موفق
            inviter_id = reward_inviter(user_id)
            if inviter_id:
                try:
                    await context.bot.send_message(
                        chat_id=inviter_id,
                        text=(
                            "🎉 *تبریک!* یک نفر با لینک دعوت شما احراز هویت کرد.\n\n"
                            "🎁 *پاداش شما:*\n"
                            "💰 ۴٬۰۰۰ تومان به کیف پول\n"
                            "❓ ۳ سوال اضافه"
                        ),
                        parse_mode="Markdown"
                    )
                except:
                    pass

            # ⚠️ فقط درخواست عکس کارت - بدون متن طولانی
            await update.message.reply_text(
                "✅ شماره شما با موفقیت تأیید شد!\n\n"
                "📷 حالا لطفاً *عکس کارت بانکی* خود را ارسال کنید.\n"
                "⚠️ فقط کارت‌هایی که به نام شما هستند.\n"
                "⚠️ شماره CVV2 را در عکس بپوشانید.",
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await update.message.reply_text(
                "❌ کد وارد شده اشتباه است.\n\n"
                "لطفاً دوباره تلاش کنید.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔴 لغو احراز هویت", callback_data="cancel_auth", style="danger")]
                ])
            )
        return

    # ---- شماره کارت ----
    if context.user_data.get('awaiting_card_number'):
        if text and text.isdigit() and len(text) == 16:
            context.user_data['awaiting_card_number'] = False
            card_photo = context.user_data.get('card_photo')

            if card_photo:
                card_id = add_card(user_id, text, user.first_name or "کاربر", card_photo)
                context.user_data.pop('card_photo', None)

                await update.message.reply_text(
                    "✅ کارت شما ثبت شد.\n"
                    "⏳ کارت در انتظار تأیید قرار دارد.",
                    reply_markup=get_main_menu_keyboard()
                )

                user_info = get_user_info(user_id)
                try:
                    await context.bot.send_photo(
                        chat_id=ACCOUNTING_GROUP,
                        photo=card_photo,
                        caption=(
                            f"📌 احراز کارت جدید\n\n"
                            f"👤 کاربر: @{user.username or 'ندارد'}\n"
                            f"🆔 آیدی: {user_id}\n"
                            f"📱 شماره: {user_info.get('phone', 'نامشخص') if user_info else 'نامشخص'}\n"
                            f"💳 شماره کارت: {text}\n"
                            f"👤 نام: {user.first_name or ''}"
                        ),
                        reply_markup=InlineKeyboardMarkup([
                            [
                                InlineKeyboardButton("✅ تأیید کارت", callback_data=f"acc_verify_{card_id}", style="success"),
                                InlineKeyboardButton("❌ رد کارت", callback_data=f"acc_reject_{card_id}", style="danger"),
                            ]
                        ])
                    )
                except Exception as e:
                    print(f"Error sending to accounting: {e}")
            else:
                context.user_data['awaiting_card_photo'] = True
                context.user_data['card_number_temp'] = text
                await update.message.reply_text(
                    "📷 لطفاً عکس کارت خود را ارسال کنید.\n\n"
                    "⚠️ شماره CVV2 را در عکس بپوشانید."
                )
        else:
            await update.message.reply_text("⚠️ شماره کارت باید ۱۶ رقم عددی باشد.")
        return

    # ---- کد تخفیف ----
    if context.user_data.get('awaiting_discount_code'):
        context.user_data['awaiting_discount_code'] = False
        discount_code = text.strip()

        code_data = get_discount_code(discount_code)
        if not code_data:
            await update.message.reply_text(
                "⚠️ کد تخفیف نامعتبر است.",
                reply_markup=get_main_menu_keyboard()
            )
            return

        use_discount_code(discount_code)
        await update.message.reply_text(
            f"✅ کد تخفیف {discount_code} اعمال شد.\n\n"
            f"📊 درصد: {code_data[2]}%\n"
            f"💰 مبلغ: {code_data[3]:,} تومان"
        )
        return

    # ---- تعداد سوال ----
    if context.user_data.get('awaiting_question_count'):
        if text and text.isdigit():
            count = int(text)
            if count < 1:
                await update.message.reply_text("⚠️ تعداد باید حداقل 1 باشد.")
                return

            price_per = 30000 if count < 15 else 25000
            total = count * price_per
            context.user_data['awaiting_question_count'] = False
            context.user_data['question_purchase'] = {'count': count, 'total': total}

            cards = get_verified_cards(user_id)
            if not cards:
                await update.message.reply_text(
                    "❗ شما کارت تأیید شده ندارید. ابتدا احراز هویت کنید.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🪪 احراز هویت", callback_data="auth", style="primary")]
                    ])
                )
                return

            wallet = user_info['wallet']
            remaining = total - wallet if wallet < total else 0
            context.user_data['question_purchase_amount'] = total

            invoice_text = (
                f"🧾 فاکتور خرید سوال\n\n"
                f"❓ تعداد سوال: {count}\n"
                f"💰 قیمت هر سوال: {price_per:,} تومان\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"💰 مبلغ کل: {total:,} تومان\n"
                f"💳 موجودی کیف پول: {wallet:,} تومان\n"
                f"➖ کسر از کیف پول: {min(wallet, total):,} تومان\n"
                f"✅ مبلغ قابل پرداخت: {remaining:,} تومان\n"
                f"━━━━━━━━━━━━━━━━━━\n\n"
                f"💳 لطفاً کارت پرداخت را انتخاب کنید:"
            )

            await update.message.reply_text(
                invoice_text,
                reply_markup=get_cards_for_payment(cards)
            )
        else:
            await update.message.reply_text("⚠️ لطفاً یک عدد معتبر وارد کنید.")
        return

    # ============================================
    # منوی اصلی
    # ============================================

    if text == "👤 حساب من":
        now = get_shamsi_now()
        await update.message.reply_text(
            get_account_text(user_info, user_id, now),
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )

    elif text == "🤝 دعوت دوستان":
        stats = get_user_referral_stats(user_id)
        referral_link = f"{BOT_LINK}{user_id}"

        try:
            await update.message.reply_text(
                INVITE_TEXT_1.format(invite_link=referral_link),
                disable_web_page_preview=True
            )
            await update.message.reply_text(
                INVITE_TEXT_2,
                parse_mode="Markdown"
            )
            await update.message.reply_text(
                f"📊 *آمار زیرمجموعه‌های شما:*\n\n"
                f"✅ کامل (احراز هویت شده): {stats['complete']}\n"
                f"⏳ ناقص (احراز هویت نشده): {stats['incomplete']}\n"
                f"💰 پاداش کامل: {stats['complete'] * 4000:,} تومان",
                reply_markup=get_main_menu_keyboard(),
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Error in invite: {e}")
            await update.message.reply_text(
                f"⚠️ خطا در نمایش لینک دعوت.\n\n"
                f"🔗 لینک دعوت شما: {referral_link}",
                reply_markup=get_main_menu_keyboard()
            )

    elif text == "📋 درباره ما":
        if ABOUT_IMAGE_URL:
            try:
                await update.message.reply_photo(
                    photo=ABOUT_IMAGE_URL,
                    caption=ABOUT_US_TEXT,
                    reply_markup=get_about_buttons(),
                    parse_mode="Markdown"
                )
            except:
                await update.message.reply_text(
                    ABOUT_US_TEXT,
                    reply_markup=get_about_buttons(),
                    parse_mode="Markdown"
                )
        else:
            await update.message.reply_text(
                ABOUT_US_TEXT,
                reply_markup=get_about_buttons(),
                parse_mode="Markdown"
            )

    elif text == "📖 راهنما":
        await update.message.reply_text(HELP_TEXT, reply_markup=get_main_menu_keyboard())

    elif text == "🆘 قوانین":
        await update.message.reply_text(RULES_TEXT, reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")

    elif text == "☎️ پشتیبانی":
        open_ticket = get_user_open_ticket(user_id)
        if open_ticket:
            ticket_id, ticket_code, status = open_ticket
            status_map = {
                'waiting': '⏳ در انتظار پشتیبان',
                'taken': '👨‍💻 در حال بررسی',
                'answered': '✅ پاسخ داده شده'
            }
            await update.message.reply_text(
                SUPPORT_HAS_OPEN_TICKET.format(
                    ticket_code=ticket_code,
                    status=status_map.get(status, status)
                ),
                reply_markup=get_user_ticket_buttons(ticket_id),
                parse_mode="Markdown"
            )
        else:
            context.user_data['awaiting_support_message'] = True
            context.user_data.pop('support_message', None)
            await update.message.reply_text(
                SUPPORT_TEXT,
                reply_markup=get_cancel_ticket_keyboard(),
                parse_mode="Markdown"
            )

    elif text == "📫 ارسال تیکت":
        user_message = context.user_data.get('support_message', '').strip()

        if context.user_data.get('awaiting_support_message'):
            if user_message:
                context.user_data['awaiting_support_message'] = False
                context.user_data.pop('support_message', None)
                ticket_id, ticket_code = create_ticket(user_id, user_message)

                try:
                    await context.bot.send_message(
                        chat_id=SUPPORT_GROUP,
                        text=(
                            f"📩 درخواست جدید پشتیبانی\n\n"
                            f"🆔 کد پیگیری: {ticket_code}\n"
                            f"👤 کاربر: @{user.username or 'ندارد'}\n"
                            f"🆔 ID: {user_id}\n"
                            f"📱 شماره: {user_info.get('phone', 'نامشخص')}\n"
                            f"🕐 زمان: {get_shamsi_now()}\n\n"
                            f"📝 پیام کاربر:\n{user_message}"
                        ),
                        reply_markup=InlineKeyboardMarkup([
                            [
                                InlineKeyboardButton("✅ پاسخ دادن", callback_data=f"sup_answer_{ticket_id}", style="success"),
                                InlineKeyboardButton("❌ بستن", callback_data=f"sup_close_{ticket_id}", style="danger"),
                            ]
                        ])
                    )
                except Exception as e:
                    print(f"Error sending to support: {e}")

                await update.message.reply_text(
                    SUPPORT_TICKET_CREATED.format(ticket_code=ticket_code),
                    reply_markup=get_main_menu_keyboard(),
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    "⚠️ لطفاً اول پیام خود را ارسال کنید.\n\n"
                    "پیام خود را بنویسید و سپس روی «📫 ارسال تیکت» بزنید.",
                    reply_markup=get_cancel_ticket_keyboard()
                )
        else:
            await update.message.reply_text(
                "⚠️ لطفاً ابتدا از منوی «☎️ پشتیبانی» اقدام کنید.",
                reply_markup=get_main_menu_keyboard()
            )

    elif text == "❌ لغو تیکت":
        context.user_data['awaiting_support_message'] = False
        context.user_data.pop('support_message', None)
        await update.message.reply_text(MAIN_MENU_TEXT, reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")

    elif context.user_data.get('awaiting_support_message') and text not in main_menu_buttons:
        context.user_data['support_message'] = text
        await update.message.reply_text(
            "✅ پیام شما دریافت شد.\n\n"
            "👇 حالا روی دکمه «📫 ارسال تیکت» بزنید.",
            reply_markup=get_cancel_ticket_keyboard()
        )

    elif text == "📚 ارسال سوال":
        if not user_info['active_package'] or user_info['active_package'] == '0':
            await update.message.reply_text(
                NO_PACKAGE_MSG,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📦 خرید پکیج", callback_data="buy_package", style="success")]
                ])
            )
        elif user_info['questions_remaining'] <= 0:
            await update.message.reply_text(
                NO_QUESTION_MSG,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("❓ خرید سوال", callback_data="buy_question", style="success")]
                ])
            )
        else:
            await update.message.reply_text(
                "📚 لطفاً درس مورد نظر خود را انتخاب کنید.",
                reply_markup=get_lesson_keyboard()
            )

    elif text == "💸 افزایش موجودی":
        await update.message.reply_text(INCREASE_BALANCE_TEXT, reply_markup=get_balance_buttons())

    elif text in ["🧬 زیست", "🧪 شیمی", "⚡️ فیزیک", "📐 ریاضی"]:
        if not user_info['active_package'] or user_info['active_package'] == '0':
            await update.message.reply_text(NO_PACKAGE_MSG)
        elif user_info['questions_remaining'] <= 0:
            await update.message.reply_text(NO_QUESTION_MSG)
        else:
            subject_name = text.split(" ")[1] if " " in text else text
            context.user_data['selected_subject'] = subject_name
            context.user_data['awaiting_question'] = True
            await update.message.reply_text(
                "📩 لطفاً سوال خود را ارسال کنید.\n\n"
                "❗ سوال خود را همراه با پاسخنامه سوال ارسال کنید.",
                reply_markup=get_cancel_question_keyboard()
            )

    elif text == "❌ لغو سوال":
        clear_user_states(context)
        await update.message.reply_text("❌ سوال لغو شد.", reply_markup=get_main_menu_keyboard())

    elif text == "🔙 برگشت":
        clear_user_states(context)
        await update.message.reply_text(MAIN_MENU_TEXT, reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")

    elif text == "🏠 منوی اصلی":
        clear_user_states(context)
        await update.message.reply_text(
            MAIN_MENU_TEXT,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )

    elif context.user_data.get('awaiting_description'):
        context.user_data['awaiting_description'] = False
        subject = context.user_data.get('selected_subject', 'زیست')
        question_text = context.user_data.get('question_text', '')

        question_id, code = create_question(
            user_id, subject, question_text, text,
            context.user_data.get('question_file')
        )

        new_remaining = user_info['questions_remaining'] - 1
        new_used = user_info['questions_used'] + 1
        update_user(user_id, questions_remaining=new_remaining, questions_used=new_used)

        await update.message.reply_text(
            f"✅ سوال شما با موفقیت ثبت شد.\n\n"
            f"🆔 کد پیگیری: {code}\n\n"
            f"📤 سوال برای دبیر مربوطه ارسال شد.",
            reply_markup=get_main_menu_keyboard()
        )

        subject_info = SUBJECTS.get(subject)
        if subject_info:
            try:
                await context.bot.send_message(
                    chat_id=subject_info['group'],
                    text=(
                        f"📚 درس: {subject}\n"
                        f"👤 دانش‌آموز: @{user.username or 'ندارد'}\n"
                        f"🆔 کد سوال: {code}\n"
                        f"🕐 زمان: {get_shamsi_now()}\n\n"
                        f"📝 توضیح دانش‌آموز:\n{text}"
                    ),
                    reply_markup=InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton("✅ پاسخ دادن", callback_data=f"t_answer_{question_id}", style="success"),
                            InlineKeyboardButton("❌ بستن", callback_data=f"t_close_{question_id}", style="danger"),
                        ]
                    ])
                )
            except Exception as e:
                print(f"Error sending to teachers: {e}")

        clear_user_states(context)

    elif context.user_data.get('awaiting_question'):
        context.user_data['awaiting_question'] = False
        context.user_data['question_text'] = text
        context.user_data['awaiting_description'] = True
        await update.message.reply_text(
            "✍️ لطفاً مشکل خود را توضیح دهید.",
            reply_markup=get_cancel_question_keyboard()
        )

    else:
        await update.message.reply_text(
            "⚠️ لطفاً از گزینه‌های منو استفاده کنید.",
            reply_markup=get_main_menu_keyboard()
        )


async def handle_about_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()