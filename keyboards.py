from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from config import DEFAULT_PACKAGES, CHANNEL_LINK


# ============================================
# جوین اجباری
# ============================================

def get_force_buttons():
    keyboard = [
        [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK, style="primary")],
        [InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_sub", style="success")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# منوی اصلی
# ============================================

def get_main_menu_keyboard():
    keyboard = [
        [KeyboardButton("📚 ارسال سوال", style="primary")],
        [KeyboardButton("💸 افزایش موجودی", style="success"), KeyboardButton("👤 حساب من", style="primary")],
        [KeyboardButton("🤝 دعوت دوستان", style="success"), KeyboardButton("☎️ پشتیبانی", style="primary")],
        [KeyboardButton("🆘 قوانین", style="danger"), KeyboardButton("📖 راهنما", style="primary")],
        [KeyboardButton("📋 درباره ما", style="primary")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_lesson_keyboard():
    keyboard = [
        [KeyboardButton("🧬 زیست", style="success"), KeyboardButton("🧪 شیمی", style="primary")],
        [KeyboardButton("⚡️ فیزیک", style="primary"), KeyboardButton("📐 ریاضی", style="success")],
        [KeyboardButton("🔙 برگشت", style="danger")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_back_keyboard():
    keyboard = [[KeyboardButton("🔙 برگشت", style="danger")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_cancel_question_keyboard():
    keyboard = [[KeyboardButton("❌ لغو سوال", style="danger")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_phone_share_keyboard():
    keyboard = [[KeyboardButton("📱 اشتراک‌گذاری شماره من", request_contact=True, style="success")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


def get_cancel_ticket_keyboard():
    keyboard = [[KeyboardButton("❌ لغو تیکت", style="danger")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ============================================
# افزایش موجودی
# ============================================

def get_balance_buttons():
    keyboard = [
        [InlineKeyboardButton("🪪 احراز هویت", callback_data="auth", style="primary")],
        [InlineKeyboardButton("📦 خرید پکیج", callback_data="buy_package", style="success")],
        [InlineKeyboardButton("❓ خرید سوال", callback_data="buy_question", style="success")],
        [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main", style="danger")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_auth_buttons():
    keyboard = [
        [InlineKeyboardButton("🧾 لیست کارت‌ها", callback_data="card_list", style="primary")],
        [InlineKeyboardButton("➕ افزودن کارت", callback_data="add_card", style="success")],
        [InlineKeyboardButton("➖ حذف کارت", callback_data="remove_card", style="danger")],
        [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main", style="danger")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_about_buttons():
    keyboard = [
        [InlineKeyboardButton("🧬 زیست‌شناسی", callback_data="about_biology", style="success")],
        [InlineKeyboardButton("🧪 شیمی", callback_data="about_chemistry", style="primary")],
        [InlineKeyboardButton("⚡️ فیزیک", callback_data="about_physics", style="primary")],
        [InlineKeyboardButton("📐 ریاضی", callback_data="about_math", style="success")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_teacher_navigation_buttons(subject, current_index, total):
    keyboard = []
    row = []

    if total > 1:
        if current_index > 0:
            row.append(InlineKeyboardButton(
                "◀️ دبیر قبلی",
                callback_data=f"teacher_prev_{subject}_{current_index-1}",
                style="primary"
            ))
        if current_index < total - 1:
            row.append(InlineKeyboardButton(
                "دبیر بعدی ▶️",
                callback_data=f"teacher_next_{subject}_{current_index+1}",
                style="primary"
            ))
        if row:
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton(
            f"👨‍🏫 دبیر {current_index+1} از {total}",
            callback_data="noop",
            style="success"
        )])

    keyboard.append([InlineKeyboardButton(
        "🔙 بازگشت به لیست دبیران",
        callback_data="about_back",
        style="danger"
    )])
    return InlineKeyboardMarkup(keyboard)


def get_packages_buttons(has_start_package=False):
    keyboard = []
    for pkg in DEFAULT_PACKAGES:
        if pkg['is_start'] and has_start_package:
            continue

        if pkg['is_start']:
            keyboard.append([InlineKeyboardButton(
                f"🎁 {pkg['name']} — 3 روزه رایگان",
                callback_data=f"buy_pkg_{pkg['id']}",
                style="success"
            )])
        else:
            keyboard.append([InlineKeyboardButton(
                f"🔸 {pkg['name']} | {pkg['price']:,} تومان | {pkg['questions']} سوال",
                callback_data=f"buy_pkg_{pkg['id']}",
                style="primary"
            )])
    keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="back_to_balance", style="danger")])
    return InlineKeyboardMarkup(keyboard)


def get_start_package_activated_buttons():
    keyboard = [
        [InlineKeyboardButton("🔙 بازگشت به پکیج‌ها", callback_data="back_to_packages", style="danger")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_cards_for_payment(cards):
    keyboard = []
    for card in cards:
        masked = f"{card[2][:4]} **** **** {card[2][-4:]}"
        star = "⭐ " if card[6] else ""
        keyboard.append([InlineKeyboardButton(
            f"💳 {star}{masked}",
            callback_data=f"pay_card_{card[0]}",
            style="success"
        )])
    keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="back_to_balance", style="danger")])
    return InlineKeyboardMarkup(keyboard)


def get_invoice_buttons(use_wallet=False):
    if use_wallet:
        keyboard = [
            [InlineKeyboardButton("💰 پرداخت با کیف پول", callback_data="pay_wallet", style="success")],
            [InlineKeyboardButton("🔗 پرداخت از درگاه", callback_data="pay_gateway", style="primary")],
            [InlineKeyboardButton("❌ لغو", callback_data="back_to_balance", style="danger")],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("🔗 پرداخت از درگاه", callback_data="pay_gateway", style="primary")],
            [InlineKeyboardButton("❌ لغو", callback_data="back_to_balance", style="danger")],
        ]
    return InlineKeyboardMarkup(keyboard)


def get_payment_buttons(payment_url):
    keyboard = [
        [InlineKeyboardButton("💳 ورود به درگاه پرداخت", url=payment_url, style="primary")],
        [InlineKeyboardButton("✅ پرداخت کردم", callback_data="paid_check", style="success")],
        [InlineKeyboardButton("❌ لغو", callback_data="back_to_balance", style="danger")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# دبیران - سوالات
# ============================================

def get_teacher_question_buttons(question_id):
    keyboard = [
        [InlineKeyboardButton("✅ پاسخ دادن", callback_data=f"t_answer_{question_id}", style="success")],
        [InlineKeyboardButton("❌ بستن", callback_data=f"t_close_{question_id}", style="danger")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_teacher_close_button(question_id):
    keyboard = [[InlineKeyboardButton("❌ بستن سوال", callback_data=f"t_close_{question_id}", style="danger")]]
    return InlineKeyboardMarkup(keyboard)


def get_student_answer_buttons(question_id):
    keyboard = [
        [InlineKeyboardButton("✅ متوجه شدم", callback_data=f"s_understood_{question_id}", style="success")],
        [InlineKeyboardButton("❓ سوال تکمیلی", callback_data=f"s_followup_{question_id}", style="primary")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# پشتیبانی
# ============================================

def get_support_ticket_buttons(ticket_id):
    keyboard = [
        [InlineKeyboardButton("✅ پاسخ دادن", callback_data=f"sup_answer_{ticket_id}", style="success")],
        [InlineKeyboardButton("❌ بستن", callback_data=f"sup_close_{ticket_id}", style="danger")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_support_close_button(ticket_id):
    keyboard = [[InlineKeyboardButton("❌ بستن تیکت", callback_data=f"sup_close_{ticket_id}", style="danger")]]
    return InlineKeyboardMarkup(keyboard)


def get_user_ticket_buttons(ticket_id):
    keyboard = [
        [InlineKeyboardButton("💬 ادامه صحبت", callback_data=f"user_continue_{ticket_id}", style="primary")],
        [InlineKeyboardButton("✅ بستن تیکت", callback_data=f"user_close_{ticket_id}", style="success")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_user_ticket_waiting_buttons(ticket_id):
    keyboard = [
        [InlineKeyboardButton("✅ بستن تیکت", callback_data=f"user_close_{ticket_id}", style="success")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# حسابداری
# ============================================

def get_card_verify_buttons(card_id):
    keyboard = [
        [InlineKeyboardButton("✅ تأیید کارت", callback_data=f"acc_verify_{card_id}", style="success")],
        [InlineKeyboardButton("❌ رد کارت", callback_data=f"acc_reject_{card_id}", style="danger")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_card_verified_button(card_id):
    keyboard = [[InlineKeyboardButton("✅ تأیید شده", callback_data="noop", style="success")]]
    return InlineKeyboardMarkup(keyboard)


def get_transaction_buttons(transaction_id):
    keyboard = [
        [InlineKeyboardButton("⭕ تأیید پرداخت", callback_data=f"acc_tx_ok_{transaction_id}", style="success")],
        [InlineKeyboardButton("❌ رد پرداخت", callback_data=f"acc_tx_no_{transaction_id}", style="danger")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# پنل مدیریت
# ============================================

def get_admin_panel_keyboard():
    keyboard = [
        [InlineKeyboardButton("👤 مدیریت ادمین", callback_data="adm_manage_admins", style="primary")],
        [InlineKeyboardButton("🫅🏻 مدیریت مالک", callback_data="adm_manage_owners", style="primary")],
        [InlineKeyboardButton("👨‍🏫 مدیریت دبیران", callback_data="adm_manage_teachers", style="success")],
        [InlineKeyboardButton("🧑🏻‍💻 مدیریت کادر", callback_data="adm_manage_staff", style="primary")],
        [InlineKeyboardButton("👫 مدیریت کاربران", callback_data="adm_manage_users", style="primary")],
        [InlineKeyboardButton("📊 آمار", callback_data="adm_stats", style="primary")],
        [InlineKeyboardButton("💸 صورت حساب", callback_data="adm_invoices", style="success")],
        [InlineKeyboardButton("📣 پیام همگانی", callback_data="adm_broadcast", style="primary")],
        [InlineKeyboardButton("⚙️ تنظیمات ربات", callback_data="adm_settings", style="primary")],
        [InlineKeyboardButton("🎁 هدیه", callback_data="adm_gift", style="success")],
        [InlineKeyboardButton("🚫 روشن/خاموش", callback_data="adm_toggle", style="danger")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_back_button():
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back", style="danger")]]
    return InlineKeyboardMarkup(keyboard)


def get_teacher_management_buttons():
    keyboard = [
        [InlineKeyboardButton("➕ افزودن دبیر", callback_data="adm_teacher_add", style="success")],
        [InlineKeyboardButton("🗑 حذف دبیر", callback_data="adm_teacher_remove", style="danger")],
        [InlineKeyboardButton("📋 لیست دبیران", callback_data="adm_teacher_list", style="primary")],
        [InlineKeyboardButton("🔁 اتصال دبیر به درس", callback_data="adm_teacher_connect", style="primary")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="adm_back", style="danger")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_subject_buttons(prefix=""):
    keyboard = [
        [InlineKeyboardButton("🧬 زیست", callback_data=f"{prefix}bio", style="success")],
        [InlineKeyboardButton("🧪 شیمی", callback_data=f"{prefix}chem", style="primary")],
        [InlineKeyboardButton("⚡️ فیزیک", callback_data=f"{prefix}phys", style="primary")],
        [InlineKeyboardButton("📐 ریاضی", callback_data=f"{prefix}math", style="success")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="adm_back", style="danger")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_staff_management_buttons():
    keyboard = [
        [InlineKeyboardButton("☎️ مدیریت پشتیبان‌ها", callback_data="adm_support_manage", style="primary")],
        [InlineKeyboardButton("🧮 مدیریت حسابدارها", callback_data="adm_accountant_manage", style="primary")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="adm_back", style="danger")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_user_management_buttons():
    keyboard = [
        [InlineKeyboardButton("🔍 جستجوی کاربر", callback_data="adm_user_search", style="primary")],
        [InlineKeyboardButton("🚫 مسدود / رفع مسدود", callback_data="adm_user_block", style="danger")],
        [InlineKeyboardButton("🎁 ارسال هدیه", callback_data="adm_user_gift", style="success")],
        [InlineKeyboardButton("💳 مشاهده خریدها", callback_data="adm_user_purchases", style="primary")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="adm_back", style="danger")],
    ]
    return InlineKeyboardMarkup(keyboard)