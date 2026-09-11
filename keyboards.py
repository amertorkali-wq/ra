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
    keyboard = [
        [KeyboardButton("📫 ارسال تیکت", style="success")],
        [KeyboardButton("❌ لغو تیکت", style="danger")],
    ]
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
        [
            InlineKeyboardButton("🧾 لیست کارت‌ها", callback_data="card_list", style="primary"),
            InlineKeyboardButton("➕ افزودن کارت", callback_data="add_card", style="success"),
        ],
        [
            InlineKeyboardButton("➖ حذف کارت", callback_data="remove_card", style="danger"),
            InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main", style="danger"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_cards_delete_buttons(cards):
    """دکمه‌های حذف کارت"""
    keyboard = []
    for card in cards:
        masked = f"{card[2][:4]} **** **** {card[2][-4:]}"
        keyboard.append([
            InlineKeyboardButton(
                f"🗑 حذف {masked}",
                callback_data=f"del_card_{card[0]}",
                style="danger"
            )
        ])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="auth", style="danger")])
    return InlineKeyboardMarkup(keyboard)


def get_delete_confirm_buttons(card_id):
    """دکمه تایید حذف کارت"""
    keyboard = [
        [
            InlineKeyboardButton("✅ بله، حذف شود", callback_data=f"confirm_del_card_{card_id}", style="danger"),
            InlineKeyboardButton("❌ انصراف", callback_data="auth", style="primary"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# درباره ما
# ============================================

def get_about_buttons():
    keyboard = [
        [InlineKeyboardButton("🧬 زیست‌شناسی", callback_data="about_biology", style="primary")],
        [InlineKeyboardButton("🧪 شیمی", callback_data="about_chemistry", style="primary")],
        [InlineKeyboardButton("⚡️ فیزیک", callback_data="about_physics", style="primary")],
        [InlineKeyboardButton("📐 ریاضی", callback_data="about_math", style="primary")],
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


# ============================================
# پکیج‌ها
# ============================================

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


def get_invoice_buttons(invoice_id):
    """دکمه‌های پیش‌فاکتور"""
    keyboard = [
        [
            InlineKeyboardButton("✅ پرداخت کردم", callback_data=f"paid_check_{invoice_id}", style="success"),
            InlineKeyboardButton("🎁 کد تخفیف", callback_data=f"discount_{invoice_id}", style="primary"),
        ],
        [
            InlineKeyboardButton("❌ لغو", callback_data="back_to_balance", style="danger"),
        ],
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
# پنل مدیریت - MENU → SUBMENU → ACTION
# ============================================

def get_admin_main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("👥 کاربران", callback_data="adm_section_users", style="primary"),
            InlineKeyboardButton("🎁 هدایا", callback_data="adm_section_gift", style="success"),
        ],
        [
            InlineKeyboardButton("👨‍🏫 دبیران", callback_data="adm_section_teachers", style="success"),
            InlineKeyboardButton("🧑🏻‍💻 کادر", callback_data="adm_section_staff", style="primary"),
        ],
        [
            InlineKeyboardButton("💰 امور مالی", callback_data="adm_section_finance", style="success"),
            InlineKeyboardButton("🧾 صورت‌حساب‌ها", callback_data="adm_section_invoices", style="primary"),
        ],
        [
            InlineKeyboardButton("📊 آمار", callback_data="adm_section_stats", style="primary"),
            InlineKeyboardButton("📢 پیام همگانی", callback_data="adm_section_broadcast", style="primary"),
        ],
        [
            InlineKeyboardButton("🛡 دسترسی", callback_data="adm_section_access", style="primary"),
            InlineKeyboardButton("⚙️ تنظیمات", callback_data="adm_section_settings", style="primary"),
        ],
        [
            InlineKeyboardButton("📞 لیست شماره‌ها", callback_data="adm_section_phones", style="success"),
            InlineKeyboardButton("🔴 وضعیت ربات", callback_data="adm_section_toggle", style="danger"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_back_button():
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back", style="danger")]]
    return InlineKeyboardMarkup(keyboard)


def get_admin_users_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🔍 جستجوی کاربر", callback_data="adm_user_search", style="primary"),
            InlineKeyboardButton("🚫 مسدود / رفع", callback_data="adm_user_block", style="danger"),
        ],
        [
            InlineKeyboardButton("🎁 ارسال هدیه", callback_data="adm_user_gift", style="success"),
            InlineKeyboardButton("💳 خریدها", callback_data="adm_user_purchases", style="primary"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back", style="danger"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_gift_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🎁 اهدا پکیج", callback_data="adm_gift_package", style="success"),
            InlineKeyboardButton("⏰ اهدا زمان", callback_data="adm_gift_time", style="primary"),
        ],
        [
            InlineKeyboardButton("❓ اهدا سوال", callback_data="adm_gift_question", style="success"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back", style="danger"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_teachers_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("➕ افزودن دبیر", callback_data="adm_teacher_add", style="success"),
            InlineKeyboardButton("📝 ویرایش دبیر", callback_data="adm_teacher_edit", style="primary"),
        ],
        [
            InlineKeyboardButton("🗑 حذف دبیر", callback_data="adm_teacher_remove", style="danger"),
            InlineKeyboardButton("📋 لیست دبیران", callback_data="adm_teacher_list", style="primary"),
        ],
        [
            InlineKeyboardButton("🔁 اتصال به درس", callback_data="adm_teacher_connect", style="primary"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back", style="danger"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_staff_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("☎️ پشتیبان‌ها", callback_data="adm_support_section", style="primary"),
            InlineKeyboardButton("🧮 حسابدارها", callback_data="adm_accountant_section", style="success"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back", style="danger"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_support_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("➕ افزودن پشتیبان", callback_data="adm_sup_add", style="success"),
            InlineKeyboardButton("🗑 حذف پشتیبان", callback_data="adm_sup_remove", style="danger"),
        ],
        [
            InlineKeyboardButton("📋 لیست پشتیبان‌ها", callback_data="adm_sup_list", style="primary"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به کادر", callback_data="adm_section_staff", style="danger"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_accountant_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("➕ افزودن حسابدار", callback_data="adm_acc_add", style="success"),
            InlineKeyboardButton("🗑 حذف حسابدار", callback_data="adm_acc_remove", style="danger"),
        ],
        [
            InlineKeyboardButton("📋 لیست حسابدارها", callback_data="adm_acc_list", style="primary"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به کادر", callback_data="adm_section_staff", style="danger"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_finance_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("💳 تراکنش‌ها", callback_data="adm_transactions", style="primary"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back", style="danger"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_invoices_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📋 لیست دبیران", callback_data="adm_invoices_list", style="primary"),
            InlineKeyboardButton("🧹 ریست صورت‌حساب", callback_data="adm_invoices_reset", style="danger"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back", style="danger"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_stats_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📊 آمار کامل", callback_data="adm_stats", style="primary"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back", style="danger"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_broadcast_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("✉️ همه کاربران", callback_data="adm_bc_all", style="success"),
            InlineKeyboardButton("📈 کاربران فعال", callback_data="adm_bc_active", style="primary"),
        ],
        [
            InlineKeyboardButton("💳 خریداران پکیج", callback_data="adm_bc_buyers", style="success"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back", style="danger"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_access_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("👤 ادمین‌ها", callback_data="adm_admin_section", style="primary"),
            InlineKeyboardButton("🫅🏻 مالکان", callback_data="adm_owner_section", style="primary"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back", style="danger"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_admin_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("➕ افزودن ادمین", callback_data="adm_admin_add", style="success"),
            InlineKeyboardButton("🗑 حذف ادمین", callback_data="adm_admin_remove", style="danger"),
        ],
        [
            InlineKeyboardButton("📋 لیست ادمین‌ها", callback_data="adm_admin_list", style="primary"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به دسترسی", callback_data="adm_section_access", style="danger"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_owner_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("➕ افزودن مالک", callback_data="adm_owner_add", style="success"),
            InlineKeyboardButton("🗑 حذف مالک", callback_data="adm_owner_remove", style="danger"),
        ],
        [
            InlineKeyboardButton("📋 لیست مالکان", callback_data="adm_owner_list", style="primary"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به دسترسی", callback_data="adm_section_access", style="danger"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_settings_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("👥 جوین اجباری", callback_data="adm_set_force", style="primary"),
            InlineKeyboardButton("📝 متن‌ها", callback_data="adm_set_texts", style="primary"),
        ],
        [
            InlineKeyboardButton("💰 تعرفه‌ها", callback_data="adm_set_prices", style="success"),
            InlineKeyboardButton("🗂 گروه‌ها", callback_data="adm_set_groups", style="primary"),
        ],
        [
            InlineKeyboardButton("📚 دروس", callback_data="adm_set_subjects", style="primary"),
            InlineKeyboardButton("🎛 دکمه‌ها", callback_data="adm_set_buttons", style="primary"),
        ],
        [
            InlineKeyboardButton("🔧 عملکرد", callback_data="adm_set_performance", style="primary"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back", style="danger"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_toggle_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🟢 روشن کردن", callback_data="adm_toggle_on", style="success"),
            InlineKeyboardButton("🔴 خاموش کردن", callback_data="adm_toggle_off", style="danger"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back", style="danger"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_phones_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📊 تعداد شماره‌ها", callback_data="adm_phones_count", style="primary"),
        ],
        [
            InlineKeyboardButton("📁 خروجی CSV", callback_data="adm_phones_csv", style="success"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back", style="danger"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_confirm_cancel_buttons(action, id_):
    keyboard = [
        [
            InlineKeyboardButton("✅ تایید", callback_data=f"adm_confirm_{action}_{id_}", style="success"),
            InlineKeyboardButton("❌ لغو", callback_data="adm_back", style="danger"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)