from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from config import DEFAULT_PACKAGES, CHANNEL_LINK


# ============================================
# دکمه‌های جوین اجباری
# ============================================

def get_force_buttons():
    keyboard = [
        [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_sub")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# منوی اصلی (Reply Keyboard)
# ============================================

def get_main_menu_keyboard():
    keyboard = [
        [KeyboardButton("📚 ارسال سوال"), KeyboardButton("💸 افزایش موجودی")],
        [KeyboardButton("👤 حساب من"), KeyboardButton("🤝 دعوت دوستان")],
        [KeyboardButton("☎️ پشتیبانی"), KeyboardButton("📋 درباره ما")],
        [KeyboardButton("🆘 قوانین"), KeyboardButton("📖 راهنما")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_lesson_keyboard():
    keyboard = [
        [KeyboardButton("🧬 زیست"), KeyboardButton("🧪 شیمی")],
        [KeyboardButton("⚡️ فیزیک"), KeyboardButton("📐 ریاضی")],
        [KeyboardButton("🔙 برگشت")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_back_keyboard():
    keyboard = [[KeyboardButton("🔙 برگشت")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_cancel_question_keyboard():
    keyboard = [[KeyboardButton("❌ لغو سوال")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ============================================
# دکمه‌های شیشه‌ای (Inline)
# ============================================

def get_balance_buttons():
    keyboard = [
        [InlineKeyboardButton("احراز هویت 🪪", callback_data="auth")],
        [InlineKeyboardButton("خرید پکیج 📦", callback_data="buy_package")],
        [InlineKeyboardButton("خرید سوال ❓", callback_data="buy_question")],
        [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_auth_buttons():
    keyboard = [
        [InlineKeyboardButton("لیست کارت‌ها 🧾", callback_data="card_list")],
        [InlineKeyboardButton("افزودن کارت ➕", callback_data="add_card")],
        [InlineKeyboardButton("حذف کارت ➖", callback_data="remove_card")],
        [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_about_buttons():
    keyboard = [
        [InlineKeyboardButton("🧬 زیست", callback_data="about_biology")],
        [InlineKeyboardButton("🧪 شیمی", callback_data="about_chemistry")],
        [InlineKeyboardButton("⚡️ فیزیک", callback_data="about_physics")],
        [InlineKeyboardButton("📐 ریاضی", callback_data="about_math")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_packages_buttons():
    keyboard = []
    for pkg in DEFAULT_PACKAGES:
        if pkg['is_start']:
            keyboard.append([InlineKeyboardButton(f"🎁 {pkg['name']}", callback_data=f"buy_pkg_{pkg['id']}")])
        else:
            keyboard.append([InlineKeyboardButton(
                f"🟡 {pkg['name']} | {pkg['price']:,} تومان | {pkg['questions']} سوال",
                callback_data=f"buy_pkg_{pkg['id']}"
            )])
    keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="back_to_balance")])
    return InlineKeyboardMarkup(keyboard)


def get_cards_for_payment(cards):
    keyboard = []
    for card in cards:
        masked = f"{card[2][:4]} **** **** {card[2][-4:]}"
        keyboard.append([InlineKeyboardButton(f"💳 {masked}", callback_data=f"pay_card_{card[0]}")])
    keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="back_to_balance")])
    return InlineKeyboardMarkup(keyboard)


def get_invoice_buttons(use_wallet=False):
    if use_wallet:
        keyboard = [
            [InlineKeyboardButton("💰 پرداخت با کیف پول", callback_data="pay_wallet")],
            [InlineKeyboardButton("🔗 پرداخت از درگاه", callback_data="pay_gateway")],
            [InlineKeyboardButton("❌ لغو", callback_data="back_to_balance")],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("🔗 ورود به درگاه پرداخت", callback_data="pay_gateway")],
            [InlineKeyboardButton("✅ پرداخت کردم", callback_data="paid_check")],
            [InlineKeyboardButton("❌ لغو", callback_data="back_to_balance")],
        ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# دکمه‌های سوال در گروه دبیران
# ============================================

def get_teacher_question_buttons(question_id):
    keyboard = [
        [InlineKeyboardButton("پاسخ دادن ✅", callback_data=f"t_answer_{question_id}")],
        [InlineKeyboardButton("بستن ❌", callback_data=f"t_close_{question_id}")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_teacher_close_button(question_id):
    keyboard = [[InlineKeyboardButton("بستن ❌", callback_data=f"t_close_{question_id}")]]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# دکمه‌های دانش‌آموز بعد از پاسخ
# ============================================

def get_student_answer_buttons(question_id):
    keyboard = [
        [InlineKeyboardButton("متوجه شدم ✅", callback_data=f"s_understood_{question_id}")],
        [InlineKeyboardButton("سوال تکمیلی ❓", callback_data=f"s_followup_{question_id}")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# دکمه‌های پشتیبانی
# ============================================

def get_support_ticket_buttons(ticket_id):
    keyboard = [
        [InlineKeyboardButton("پاسخ دادن ✅", callback_data=f"sup_answer_{ticket_id}")],
        [InlineKeyboardButton("بستن ❌", callback_data=f"sup_close_{ticket_id}")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# دکمه‌های حسابداری
# ============================================

def get_card_verify_buttons(card_id):
    keyboard = [
        [InlineKeyboardButton("تایید کارت ✅", callback_data=f"acc_verify_{card_id}")],
        [InlineKeyboardButton("رد کارت ❌", callback_data=f"acc_reject_{card_id}")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_transaction_buttons(transaction_id):
    keyboard = [
        [InlineKeyboardButton("تایید پرداخت ⭕", callback_data=f"acc_tx_ok_{transaction_id}")],
        [InlineKeyboardButton("رد پرداخت ❌", callback_data=f"acc_tx_no_{transaction_id}")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# دکمه‌های پنل مدیریت
# ============================================

def get_admin_panel_keyboard():
    keyboard = [
        [InlineKeyboardButton("👤 مدیریت ادمین", callback_data="adm_manage_admins")],
        [InlineKeyboardButton("🫅🏻 مدیریت مالک", callback_data="adm_manage_owners")],
        [InlineKeyboardButton("👨‍🏫 مدیریت دبیران", callback_data="adm_manage_teachers")],
        [InlineKeyboardButton("🧑🏻‍💻 مدیریت کادر", callback_data="adm_manage_staff")],
        [InlineKeyboardButton("👫 مدیریت کاربران", callback_data="adm_manage_users")],
        [InlineKeyboardButton("📊 آمار", callback_data="adm_stats")],
        [InlineKeyboardButton("💸 صورت حساب", callback_data="adm_invoices")],
        [InlineKeyboardButton("📣 پیام همگانی", callback_data="adm_broadcast")],
        [InlineKeyboardButton("⚙️ تنظیمات ربات", callback_data="adm_settings")],
        [InlineKeyboardButton("🎁 هدیه", callback_data="adm_gift")],
        [InlineKeyboardButton("🚫 روشن/خاموش", callback_data="adm_toggle")],
    ]
    return InlineKeyboardMarkup(keyboard)
