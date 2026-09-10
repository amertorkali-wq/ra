import random
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import (
    CHANNEL_ID, BOT_LINK, DEFAULT_PACKAGES,
    SUBJECTS, ABOUT_IMAGE_URL, ACCOUNTING_GROUP, SUPPORT_GROUP,
    SMSIR_API_KEY, SMSIR_TEMPLATE_ID, SMSIR_LINE_NUMBER
)
from database import (
    get_user, create_user, update_user, get_user_cards, get_verified_cards,
    add_card, delete_card, create_question, create_ticket, add_transaction,
    reward_inviter, get_shamsi_now, get_shamsi_future_date,
    set_verification_code, get_verification_code
)
from keyboards import (
    get_force_buttons, get_main_menu_keyboard, get_lesson_keyboard,
    get_balance_buttons, get_auth_buttons, get_about_buttons,
    get_packages_buttons, get_cards_for_payment, get_invoice_buttons,
    get_back_keyboard, get_cancel_question_keyboard, get_phone_share_keyboard
)
from texts import (
    FORCE_MSG, NOT_MEMBER_MSG, WELCOME_MSG, MAIN_MENU_TEXT,
    INCREASE_BALANCE_TEXT, AUTH_TEXT, ABOUT_US_TEXT, PACKAGES_TEXT,
    BUY_QUESTION_TEXT, NO_PACKAGE_MSG, NO_QUESTION_MSG, SUPPORT_TEXT,
    INVITE_TEXT_1, INVITE_TEXT_2, RULES_TEXT, HELP_TEXT,
    ADD_CARD_TEXT, CARD_NUMBER_REQUEST, CARD_REGISTERED,
    AUTH_PHONE_REQUEST, AUTH_CODE_REQUEST, AUTH_PHONE_VERIFIED,
    get_account_text
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
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        result = response.json()
        print(f"SMS.ir Response: {result}")
        return result.get("status") == 1
    except Exception as e:
        print(f"SMS Error: {e}")
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
        'verification_code': user[5],
        'phone_verified': user[6],
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


# ============================================
# /start
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

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
        if is_new:
            inviter_id = reward_inviter(user_id)
            if inviter_id:
                try:
                    await context.bot.send_message(
                        chat_id=inviter_id,
                        text=(
                            "🎉 *تبریک!* یک نفر با لینک دعوت شما وارد ربات شد و در کانال عضو شد.\n\n"
                            "🎁 *پاداش شما:*\n"
                            "💰 ۴٬۰۰۰ تومان به کیف پول\n"
                            "❓ ۳ سوال اضافه"
                        ),
                        parse_mode="Markdown"
                    )
                except:
                    pass

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
        inviter_id = reward_inviter(user_id)
        if inviter_id:
            try:
                await context.bot.send_message(
                    chat_id=inviter_id,
                    text=(
                        "🎉 *تبریک!* یک نفر با لینک دعوت شما وارد ربات شد و در کانال عضو شد.\n\n"
                        "🎁 *پاداش شما:*\n"
                        "💰 ۴٬۰۰۰ تومان به کیف پول\n"
                        "❓ ۳ سوال اضافه"
                    ),
                    parse_mode="Markdown"
                )
            except:
                pass

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

    if data == "auth":
        await query.edit_message_text(
            AUTH_TEXT,
            reply_markup=get_auth_buttons(),
            parse_mode="Markdown"
        )

    elif data == "buy_package":
        cards = get_verified_cards(user_id)
        if not cards:
            await query.edit_message_text(
                "❗ *شما هنوز کارت بانکی تأیید شده‌ای ندارید.*\n\n"
                "لطفاً از بخش «احراز هویت» اقدام کنید.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("احراز هویت 🪪", callback_data="auth")]
                ]),
                parse_mode="Markdown"
            )
        else:
            has_start = user_info['has_start_package'] == 1
            await query.edit_message_text(
                PACKAGES_TEXT,
                reply_markup=get_packages_buttons(has_start_package=has_start),
                parse_mode="Markdown"
            )

    elif data == "buy_question":
        await query.edit_message_text(
            BUY_QUESTION_TEXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 برگشت", callback_data="back_to_balance")]
            ])
        )
        context.user_data['awaiting_question_count'] = True

    elif data == "back_to_main":
        try:
            await query.message.delete()
        except:
            pass
        await query.message.reply_text(
            MAIN_MENU_TEXT,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )

    elif data == "back_to_balance":
        await query.edit_message_text(
            INCREASE_BALANCE_TEXT,
            reply_markup=get_balance_buttons()
        )

    elif data.startswith("buy_pkg_"):
        pkg_id = int(data.split("_")[2])
        pkg = next((p for p in DEFAULT_PACKAGES if p['id'] == pkg_id), None)

        if not pkg:
            await query.edit_message_text("⚠️ پکیج یافت نشد.")
            return

        if pkg['is_start']:
            if user_info['has_start_package']:
                await query.edit_message_text(
                    "⚠️ شما قبلاً پکیج استارت را استفاده کرده‌اید.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 برگشت", callback_data="back_to_balance")]
                    ])
                )
                return

            expire_date = get_shamsi_future_date(pkg['days'])
            update_user(
                user_id,
                active_package=pkg['name'],
                package_expire_date=expire_date,
                questions_remaining=user_info['questions_remaining'] + pkg['questions'],
                has_start_package=1
            )
            await query.edit_message_text(
                f"🎉 *پکیج استارت برای شما فعال شد!*\n\n"
                f"📦 پکیج: {pkg['name']}\n"
                f"❓ تعداد سوال: {pkg['questions']}\n"
                f"⏳ اعتبار تا: {expire_date}",
                parse_mode="Markdown"
            )
            return

        cards = get_verified_cards(user_id)
        if not cards:
            await query.edit_message_text(
                "❗ شما کارت تأیید شده ندارید. ابتدا احراز هویت کنید.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("احراز هویت 🪪", callback_data="auth")]
                ])
            )
            return

        context.user_data['selected_package'] = pkg

        await query.edit_message_text(
            f"💳 *لطفاً کارت بانکی که قصد پرداخت با آن را دارید انتخاب کنید.*\n\n"
            f"📦 پکیج انتخابی: {pkg['name']}\n"
            f"💰 مبلغ: {pkg['price']:,} تومان\n"
            f"❓ تعداد سوال: {pkg['questions']}",
            reply_markup=get_cards_for_payment(cards),
            parse_mode="Markdown"
        )

    elif data.startswith("pay_card_"):
        card_id = int(data.split("_")[2])
        pkg = context.user_data.get('selected_package')

        if not pkg:
            await query.edit_message_text("⚠️ خطا! لطفاً دوباره تلاش کنید.")
            return

        wallet = user_info['wallet']
        total_price = pkg['price']

        context.user_data['selected_card_id'] = card_id

        if wallet >= total_price and total_price > 0:
            await query.edit_message_text(
                f"🧾 *فاکتور شما ایجاد شد*\n\n"
                f"📦 نوع پکیج: {pkg['name']}\n"
                f"❓ تعداد سوال: {pkg['questions']}\n\n"
                f"💰 مبلغ فاکتور: {total_price:,} تومان\n\n"
                f"💳 موجودی کیف پول: {wallet:,} تومان\n\n"
                f"✅ کیف پول شما کافی است. لطفاً روش پرداخت را انتخاب کنید:",
                reply_markup=get_invoice_buttons(use_wallet=True),
                parse_mode="Markdown"
            )
        else:
            remaining = total_price - wallet if total_price > 0 else 0
            await query.edit_message_text(
                f"🧾 *فاکتور شما ایجاد شد*\n\n"
                f"📦 نوع پکیج: {pkg['name']}\n"
                f"❓ تعداد سوال: {pkg['questions']}\n\n"
                f"💰 مبلغ فاکتور: {total_price:,} تومان\n\n"
                f"💳 موجودی کیف پول: {wallet:,} تومان\n"
                f"➖ کسر از کیف پول: {wallet:,} تومان\n\n"
                f"✅ مبلغ قابل پرداخت: {remaining:,} تومان",
                reply_markup=get_invoice_buttons(use_wallet=False),
                parse_mode="Markdown"
            )

    elif data == "pay_wallet":
        pkg = context.user_data.get('selected_package')
        if pkg:
            new_wallet = user_info['wallet'] - pkg['price']
            new_questions = user_info['questions_remaining'] + pkg['questions']
            expire_date = get_shamsi_future_date(pkg['days'])

            update_user(
                user_id,
                wallet=new_wallet,
                questions_remaining=new_questions,
                active_package=pkg['name'],
                package_expire_date=expire_date
            )

            add_transaction(user_id, pkg['price'], "wallet", "-", "success", "package")

            await query.edit_message_text(
                f"✅ *پرداخت با کیف پول انجام شد.*\n\n"
                f"📦 سفارش شما با موفقیت ثبت شد.\n\n"
                f"🎁 پکیج فعال: {pkg['name']}\n"
                f"📚 سوالات اضافه شده: {pkg['questions']}\n"
                f"⏳ اعتبار تا: {expire_date}",
                parse_mode="Markdown"
            )

    elif data == "pay_gateway":
        await query.edit_message_text(
            "🔗 در حال انتقال به درگاه پرداخت...\n\n"
            "⚠️ درگاه زرین‌پال هنوز متصل نشده است.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 برگشت", callback_data="back_to_balance")]
            ])
        )

    elif data == "paid_check":
        await query.edit_message_text(
            "⏳ در حال بررسی پرداخت...\n\n"
            "⚠️ درگاه زرین‌پال هنوز متصل نشده است."
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

    if data == "card_list":
        cards = get_user_cards(user_id)
        if cards:
            text = "🧾 *لیست کارت‌های شما:*\n\n"
            for i, card in enumerate(cards):
                masked = f"{card[2][:4]} **** **** {card[2][-4:]}"
                status = "✅ تأیید شده" if card[5] else "⏳ در انتظار تأیید"
                text += f"{i+1}️⃣ `{masked}`\n   وضعیت: {status}\n\n"
        else:
            text = "🧾 *شما هیچ کارتی ثبت نکرده‌اید.*"
        await query.edit_message_text(text, reply_markup=get_auth_buttons(), parse_mode="Markdown")

    elif data == "add_card":
        # بررسی شماره تأیید شده
        if not user_info['phone_verified']:
            await query.edit_message_text(
                AUTH_PHONE_REQUEST,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 برگشت", callback_data="auth")]
                ]),
                parse_mode="Markdown"
            )
            # ارسال کیبورد اشتراک‌گذاری شماره
            await query.message.reply_text(
                "👇 لطفاً روی دکمه زیر بزنید:",
                reply_markup=get_phone_share_keyboard()
            )
            context.user_data['awaiting_auth_phone'] = True
        else:
            # شماره تأیید شده، برو به مرحله عکس کارت
            await query.edit_message_text(
                ADD_CARD_TEXT,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 برگشت", callback_data="auth")]
                ]),
                parse_mode="Markdown"
            )
            context.user_data['awaiting_card_photo'] = True

    elif data == "remove_card":
        cards = get_user_cards(user_id)
        if not cards:
            await query.edit_message_text(
                "⚠️ *شما هیچ کارتی برای حذف ندارید.*",
                reply_markup=get_auth_buttons(),
                parse_mode="Markdown"
            )
        else:
            keyboard = []
            for card in cards:
                masked = f"****{card[2][-4:]}"
                keyboard.append([InlineKeyboardButton(f"🗑 {masked}", callback_data=f"del_card_{card[0]}")])
            keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="auth")])
            await query.edit_message_text(
                "🗑 *کارت مورد نظر برای حذف را انتخاب کنید:*",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )

    elif data.startswith("del_card_"):
        card_id = int(data.split("_")[2])
        delete_card(card_id)
        await query.edit_message_text(
            "✅ *کارت با موفقیت حذف شد.*",
            reply_markup=get_auth_buttons(),
            parse_mode="Markdown"
        )

    elif data == "auth":
        await query.edit_message_text(
            AUTH_TEXT,
            reply_markup=get_auth_buttons(),
            parse_mode="Markdown"
        )

    elif data == "back_to_main":
        try:
            await query.message.delete()
        except:
            pass
        await query.message.reply_text(
            MAIN_MENU_TEXT,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )


async def handle_about_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()


# ============================================
# دریافت شماره تلفن (احراز هویت)
# ============================================

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    if not contact:
        return

    user_id = update.effective_user.id

    # بررسی اینکه در حالت احراز هویت هستیم
    if not context.user_data.get('awaiting_auth_phone'):
        return

    phone = contact.phone_number
    if phone.startswith("+"):
        phone = phone[1:]
    if phone.startswith("98"):
        phone = "0" + phone[2:]

    # بررسی اینکه شماره متعلق به خود کاربر باشد
    if contact.user_id and contact.user_id != user_id:
        await update.message.reply_text(
            "⚠️ *لطفاً فقط شماره خودتان را ارسال کنید.*",
            parse_mode="Markdown"
        )
        return

    update_user(user_id, phone=phone)

    code = str(random.randint(10000, 99999))
    set_verification_code(user_id, code)

    print(f"📱 Sending SMS to {phone} with code {code}")

    success = send_verification_sms(phone, code)

    if success:
        context.user_data['awaiting_auth_phone'] = False
        context.user_data['awaiting_auth_code'] = True
        await update.message.reply_text(
            AUTH_CODE_REQUEST,
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await update.message.reply_text(
            "❌ *خطا در ارسال پیامک.*\n\n"
            "لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید.",
            parse_mode="Markdown"
        )


# ============================================
# هندلر عکس
# ============================================

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if context.user_data.get('awaiting_card_photo'):
        context.user_data['card_photo'] = update.message.photo[-1].file_id
        context.user_data['awaiting_card_photo'] = False
        context.user_data['awaiting_card_number'] = True

        await update.message.reply_text(
            CARD_NUMBER_REQUEST,
            parse_mode="Markdown"
        )
        return

    if context.user_data.get('awaiting_question'):
        context.user_data['awaiting_question'] = False
        context.user_data['question_file'] = update.message.photo[-1].file_id
        context.user_data['question_text'] = update.message.caption or '[عکس]'
        context.user_data['awaiting_description'] = True
        await update.message.reply_text(
            "✍️ *لطفاً مشکل خود را توضیح دهید.*",
            reply_markup=get_cancel_question_keyboard(),
            parse_mode="Markdown"
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

    user_info = get_user_info(user_id)

    update_user(
        user_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )

    # ---- حالت انتظار کد تأیید (احراز هویت) ----
    if context.user_data.get('awaiting_auth_code'):
        entered_code = text.strip()
        stored_code = get_verification_code(user_id)

        if stored_code and entered_code == stored_code:
            context.user_data['awaiting_auth_code'] = False
            update_user(user_id, phone_verified=1)

            # حالا برو به مرحله عکس کارت
            context.user_data['awaiting_card_photo'] = True

            await update.message.reply_text(
                AUTH_PHONE_VERIFIED,
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "❌ *کد وارد شده اشتباه است.*\n\n"
                "لطفاً دوباره تلاش کنید.",
                parse_mode="Markdown"
            )
        return

    # ---- حالت انتظار شماره کارت ----
    if context.user_data.get('awaiting_card_number'):
        if text and text.isdigit() and len(text) == 16:
            card_photo = context.user_data.get('card_photo')
            card_id = add_card(user_id, text, user.first_name or "کاربر", card_photo)
            context.user_data['awaiting_card_number'] = False
            context.user_data.pop('card_photo', None)

            await update.message.reply_text(
                CARD_REGISTERED,
                parse_mode="Markdown",
                reply_markup=get_main_menu_keyboard()
            )

            try:
                await context.bot.send_photo(
                    chat_id=ACCOUNTING_GROUP,
                    photo=card_photo,
                    caption=(
                        f"📌 *احراز کارت جدید*\n\n"
                        f"👤 کاربر: @{user.username or 'ندارد'}\n"
                        f"🆔 آیدی: `{user_id}`\n"
                        f"📱 شماره: `{user_info.get('phone', 'نامشخص')}`\n"
                        f"💳 شماره کارت: `{text}`\n"
                        f"👤 نام: {user.first_name or ''} {user.last_name or ''}\n"
                        f"🕐 زمان: {get_shamsi_now()}"
                    ),
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton("تایید کارت ✅", callback_data=f"acc_verify_{card_id}"),
                            InlineKeyboardButton("رد کارت ❌", callback_data=f"acc_reject_{card_id}"),
                        ]
                    ])
                )
            except Exception as e:
                print(f"Error sending to accounting: {e}")
        else:
            await update.message.reply_text(
                "⚠️ *شماره کارت باید ۱۶ رقم عددی باشد.*\n\n"
                "لطفاً دوباره وارد کنید.",
                parse_mode="Markdown"
            )
        return

    # ---- حالت انتظار تعداد سوال ----
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
                        [InlineKeyboardButton("احراز هویت 🪪", callback_data="auth")]
                    ])
                )
                return

            await update.message.reply_text(
                f"🧾 *فاکتور خرید سوال*\n\n"
                f"❓ تعداد سوال: {count}\n"
                f"💰 قیمت هر سوال: {price_per:,} تومان\n"
                f"💰 مبلغ کل: {total:,} تومان\n\n"
                f"💳 لطفاً کارت پرداخت را انتخاب کنید:",
                reply_markup=get_cards_for_payment(cards),
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("⚠️ لطفاً یک عدد معتبر وارد کنید.")
        return

    # ---- منوی اصلی ----
    if text == "👤 حساب من":
        now = get_shamsi_now()
        await update.message.reply_text(
            get_account_text(user_info, user_id, now),
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )

    elif text == "🤝 دعوت دوستان":
        referral_link = f"{BOT_LINK}{user_id}"
        await update.message.reply_text(
            INVITE_TEXT_1.format(invite_link=referral_link),
            parse_mode="Markdown"
        )
        await update.message.reply_text(
            INVITE_TEXT_2,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
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

    elif text == "☎️ پشتیبانی":
        context.user_data['awaiting_support'] = True
        await update.message.reply_text(
            SUPPORT_TEXT,
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )

    elif text == "🆘 قوانین":
        await update.message.reply_text(
            RULES_TEXT,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )

    elif text == "📖 راهنما":
        await update.message.reply_text(
            HELP_TEXT,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )

    elif text == "📚 ارسال سوال":
        if not user_info['active_package'] or user_info['active_package'] == '0':
            await update.message.reply_text(
                NO_PACKAGE_MSG,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("خرید پکیج 📦", callback_data="buy_package")]
                ])
            )
        elif user_info['questions_remaining'] <= 0:
            await update.message.reply_text(
                NO_QUESTION_MSG,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("خرید سوال ❓", callback_data="buy_question")]
                ])
            )
        else:
            await update.message.reply_text(
                "📚 *لطفاً درس مورد نظر خود را انتخاب کنید.*",
                reply_markup=get_lesson_keyboard(),
                parse_mode="Markdown"
            )

    elif text == "💸 افزایش موجودی":
        await update.message.reply_text(
            INCREASE_BALANCE_TEXT,
            reply_markup=get_balance_buttons()
        )

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
                "📩 *لطفاً سوال خود را ارسال کنید.*\n\n"
                "❗ سوال خود را همراه با پاسخنامه سوال ارسال کنید.\n\n"
                "🚫 در این بخش ارسال ویس مجاز نیست.",
                reply_markup=get_cancel_question_keyboard(),
                parse_mode="Markdown"
            )

    elif text == "❌ لغو سوال":
        context.user_data.clear()
        await update.message.reply_text(
            "❌ *سوال لغو شد.*",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )

    elif text == "🔙 برگشت":
        context.user_data.clear()
        await update.message.reply_text(
            MAIN_MENU_TEXT,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )

    elif context.user_data.get('awaiting_support'):
        context.user_data['awaiting_support'] = False
        ticket_id, ticket_code = create_ticket(user_id, text)

        try:
            await context.bot.send_message(
                chat_id=SUPPORT_GROUP,
                text=(
                    f"📩 *درخواست جدید پشتیبانی*\n\n"
                    f"🆔 کد پیگیری: `{ticket_code}`\n"
                    f"👤 کاربر: @{user.username or 'ندارد'}\n"
                    f"🆔 ID: `{user_id}`\n"
                    f"📱 شماره: `{user_info.get('phone', 'نامشخص')}`\n"
                    f"🕐 زمان: {get_shamsi_now()}\n\n"
                    f"📝 *پیام کاربر:*\n{text}"
                ),
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("پاسخ دادن ✅", callback_data=f"sup_answer_{ticket_id}"),
                        InlineKeyboardButton("بستن ❌", callback_data=f"sup_close_{ticket_id}"),
                    ]
                ])
            )
        except Exception as e:
            print(f"Error sending to support: {e}")

        await update.message.reply_text(
            f"✅ *پیام شما با موفقیت ثبت شد.*\n\n"
            f"🆔 کد پیگیری: `{ticket_code}`\n\n"
            f"تیم پشتیبانی به زودی پیام شما را بررسی می‌کند.",
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
            f"✅ *سوال شما با موفقیت ثبت شد.*\n\n"
            f"🆔 کد پیگیری: `{code}`\n\n"
            f"📤 سوال برای دبیر مربوطه ارسال شد.\n"
            f"💠 پس از آماده شدن پاسخ از طریق همین ربات اطلاع داده خواهد شد.",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )

        subject_info = SUBJECTS.get(subject)
        if subject_info:
            try:
                await context.bot.send_message(
                    chat_id=subject_info['group'],
                    text=(
                        f"📚 *درس:* {subject}\n"
                        f"👤 دانش‌آموز: @{user.username or 'ندارد'}\n"
                        f"🆔 کد سوال: `{code}`\n"
                        f"🕐 زمان: {get_shamsi_now()}\n\n"
                        f"📝 *توضیح دانش‌آموز:*\n{text}"
                    ),
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton("پاسخ دادن ✅", callback_data=f"t_answer_{question_id}"),
                            InlineKeyboardButton("بستن ❌", callback_data=f"t_close_{question_id}"),
                        ]
                    ])
                )
            except Exception as e:
                print(f"Error sending to teachers: {e}")

        context.user_data.clear()

    elif context.user_data.get('awaiting_question'):
        context.user_data['awaiting_question'] = False
        context.user_data['question_text'] = text
        context.user_data['awaiting_description'] = True
        await update.message.reply_text(
            "✍️ *لطفاً مشکل خود را توضیح دهید.*",
            reply_markup=get_cancel_question_keyboard(),
            parse_mode="Markdown"
        )

    else:
        await update.message.reply_text(
            "⚠️ لطفاً از گزینه‌های منو استفاده کنید.",
            reply_markup=get_main_menu_keyboard()
        )