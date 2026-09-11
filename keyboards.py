from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from config import DEFAULT_PACKAGES, CHANNEL_LINK


# ============================================
# جوین اجباری
# ============================================

def get_force_buttons():
    keyboard = [
        [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_sub")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# منوی اصلی
# ============================================

def get_main_menu_keyboard():
    keyboard = [
        [KeyboardButton("📚 ارسال سوال")],
        [KeyboardButton("💸 افزایش موجودی"), KeyboardButton("👤 حساب من")],
        [KeyboardButton("🤝 دعوت دوستان"), KeyboardButton("☎️ پشتیبانی")],
        [KeyboardButton("🆘 قوانین"), KeyboardButton("📖 راهنما")],
        [KeyboardButton("📋 درباره ما")],
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


def get_phone_share_keyboard():
    keyboard = [[KeyboardButton("📱 اشتراک‌گذاری شماره من", request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


def get_cancel_ticket_keyboard():
    keyboard = [
        [KeyboardButton("📫 ارسال تیکت")],
        [KeyboardButton("❌ لغو تیکت")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ============================================
# افزایش موجودی
# ============================================

def get_balance_buttons():
    keyboard = [
        [InlineKeyboardButton("🪪 احراز هویت", callback_data="auth")],
        [InlineKeyboardButton("📦 خرید پکیج", callback_data="buy_package")],
        [InlineKeyboardButton("❓ خرید سوال", callback_data="buy_question")],
        [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_auth_buttons():
    keyboard = [
        [
            InlineKeyboardButton("🧾 لیست کارت‌ها", callback_data="card_list"),
            InlineKeyboardButton("➕ افزودن کارت", callback_data="add_card"),
        ],
        [
            InlineKeyboardButton("➖ حذف کارت", callback_data="remove_card"),
            InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_cards_delete_buttons(cards):
    keyboard = []
    for card in cards:
        masked = f"{card[2][:4]} **** **** {card[2][-4:]}"
        keyboard.append([
            InlineKeyboardButton(
                f"🗑 حذف {masked}",
                callback_data=f"del_card_{card[0]}"
            )
        ])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="auth")])
    return InlineKeyboardMarkup(keyboard)


def get_delete_confirm_buttons(card_id):
    keyboard = [
        [
            InlineKeyboardButton("✅ بله، حذف شود", callback_data=f"confirm_del_card_{card_id}"),
            InlineKeyboardButton("❌ انصراف", callback_data="auth"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# درباره ما
# ============================================

def get_about_buttons():
    keyboard = [
        [InlineKeyboardButton("🧬 زیست‌شناسی", callback_data="about_biology")],
        [InlineKeyboardButton("🧪 شیمی", callback_data="about_chemistry")],
        [InlineKeyboardButton("⚡️ فیزیک", callback_data="about_physics")],
        [InlineKeyboardButton("📐 ریاضی", callback_data="about_math")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_teacher_navigation_buttons(subject, current_index, total):
    keyboard = []
    row = []

    if total > 1:
        if current_index > 0:
            row.append(InlineKeyboardButton(
                "◀️ دبیر قبلی",
                callback_data=f"teacher_prev_{subject}_{current_index-1}"
            ))
        if current_index < total - 1:
            row.append(InlineKeyboardButton(
                "دبیر بعدی ▶️",
                callback_data=f"teacher_next_{subject}_{current_index+1}"
            ))
        if row:
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton(
            f"👨‍🏫 دبیر {current_index+1} از {total}",
            callback_data="noop"
        )])

    keyboard.append([InlineKeyboardButton(
        "🔙 بازگشت به لیست دبیران",
        callback_data="about_back"
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
                callback_data=f"buy_pkg_{pkg['id']}"
            )])
        else:
            keyboard.append([InlineKeyboardButton(
                f"🔸 {pkg['name']} | {pkg['price']:,} تومان | {pkg['questions']} سوال",
                callback_data=f"buy_pkg_{pkg['id']}"
            )])
    keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="back_to_balance")])
    return InlineKeyboardMarkup(keyboard)


def get_start_package_activated_buttons():
    keyboard = [
        [InlineKeyboardButton("🔙 بازگشت به پکیج‌ها", callback_data="back_to_packages")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_cards_for_payment(cards):
    keyboard = []
    for card in cards:
        masked = f"{card[2][:4]} **** **** {card[2][-4:]}"
        star = "⭐ " if card[6] else ""
        keyboard.append([InlineKeyboardButton(
            f"💳 {star}{masked}",
            callback_data=f"pay_card_{card[0]}"
        )])
    keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="back_to_balance")])
    return InlineKeyboardMarkup(keyboard)


def get_invoice_buttons(invoice_id):
    keyboard = [
        [
            InlineKeyboardButton("✅ پرداخت کردم", callback_data=f"paid_check_{invoice_id}"),
            InlineKeyboardButton("🎁 کد تخفیف", callback_data=f"discount_{invoice_id}"),
        ],
        [
            InlineKeyboardButton("❌ لغو", callback_data="back_to_balance"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_payment_buttons(payment_url):
    keyboard = [
        [InlineKeyboardButton("💳 ورود به درگاه پرداخت", url=payment_url)],
        [InlineKeyboardButton("✅ پرداخت کردم", callback_data="paid_check")],
        [InlineKeyboardButton("❌ لغو", callback_data="back_to_balance")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# دبیران - سوالات
# ============================================

def get_teacher_question_buttons(question_id):
    keyboard = [
        [InlineKeyboardButton("✅ پاسخ دادن", callback_data=f"t_answer_{question_id}")],
        [InlineKeyboardButton("❌ بستن", callback_data=f"t_close_{question_id}")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_teacher_close_button(question_id):
    keyboard = [[InlineKeyboardButton("❌ بستن سوال", callback_data=f"t_close_{question_id}")]]
    return InlineKeyboardMarkup(keyboard)


def get_student_answer_buttons(question_id):
    keyboard = [
        [InlineKeyboardButton("✅ متوجه شدم", callback_data=f"s_understood_{question_id}")],
        [InlineKeyboardButton("❓ سوال تکمیلی", callback_data=f"s_followup_{question_id}")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# پشتیبانی
# ============================================

def get_support_ticket_buttons(ticket_id):
    keyboard = [
        [InlineKeyboardButton("✅ پاسخ دادن", callback_data=f"sup_answer_{ticket_id}")],
        [InlineKeyboardButton("❌ بستن", callback_data=f"sup_close_{ticket_id}")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_support_close_button(ticket_id):
    keyboard = [[InlineKeyboardButton("❌ بستن تیکت", callback_data=f"sup_close_{ticket_id}")]]
    return InlineKeyboardMarkup(keyboard)


def get_user_ticket_buttons(ticket_id):
    keyboard = [
        [InlineKeyboardButton("💬 ادامه صحبت", callback_data=f"user_continue_{ticket_id}")],
        [InlineKeyboardButton("✅ بستن تیکت", callback_data=f"user_close_{ticket_id}")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_user_ticket_waiting_buttons(ticket_id):
    keyboard = [
        [InlineKeyboardButton("✅ بستن تیکت", callback_data=f"user_close_{ticket_id}")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# حسابداری
# ============================================

def get_card_verify_buttons(card_id):
    keyboard = [
        [InlineKeyboardButton("✅ تأیید کارت", callback_data=f"acc_verify_{card_id}")],
        [InlineKeyboardButton("❌ رد کارت", callback_data=f"acc_reject_{card_id}")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_card_verified_button(card_id):
    keyboard = [[InlineKeyboardButton("✅ تأیید شده", callback_data="noop")]]
    return InlineKeyboardMarkup(keyboard)


def get_transaction_buttons(transaction_id):
    keyboard = [
        [InlineKeyboardButton("⭕ تأیید پرداخت", callback_data=f"acc_tx_ok_{transaction_id}")],
        [InlineKeyboardButton("❌ رد پرداخت", callback_data=f"acc_tx_no_{transaction_id}")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# پنل مدیریت
# ============================================

def get_admin_main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("👥 کاربران", callback_data="adm_section_users"),
            InlineKeyboardButton("🎁 هدایا", callback_data="adm_section_gift"),
        ],
        [
            InlineKeyboardButton("👨‍🏫 دبیران", callback_data="adm_section_teachers"),
            InlineKeyboardButton("🧑🏻‍💻 کادر", callback_data="adm_section_staff"),
        ],
        [
            InlineKeyboardButton("💰 امور مالی", callback_data="adm_section_finance"),
            InlineKeyboardButton("🧾 صورت‌حساب‌ها", callback_data="adm_section_invoices"),
        ],
        [
            InlineKeyboardButton("📊 آمار", callback_data="adm_section_stats"),
            InlineKeyboardButton("📢 پیام همگانی", callback_data="adm_section_broadcast"),
        ],
        [
            InlineKeyboardButton("🛡 دسترسی", callback_data="adm_section_access"),
            InlineKeyboardButton("⚙️ تنظیمات", callback_data="adm_section_settings"),
        ],
        [
            InlineKeyboardButton("📞 لیست شماره‌ها", callback_data="adm_section_phones"),
            InlineKeyboardButton("🔴 وضعیت ربات", callback_data="adm_section_toggle"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_back_button():
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back")]]
    return InlineKeyboardMarkup(keyboard)


def get_admin_users_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🔍 جستجوی کاربر", callback_data="adm_user_search"),
            InlineKeyboardButton("🚫 مسدود / رفع", callback_data="adm_user_block"),
        ],
        [
            InlineKeyboardButton("🎁 ارسال هدیه", callback_data="adm_user_gift"),
            InlineKeyboardButton("💳 خریدها", callback_data="adm_user_purchases"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_gift_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🎁 اهدا پکیج", callback_data="adm_gift_package"),
            InlineKeyboardButton("⏰ اهدا زمان", callback_data="adm_gift_time"),
        ],
        [
            InlineKeyboardButton("❓ اهدا سوال", callback_data="adm_gift_question"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_teachers_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("➕ افزودن دبیر", callback_data="adm_teacher_add"),
            InlineKeyboardButton("📝 ویرایش دبیر", callback_data="adm_teacher_edit"),
        ],
        [
            InlineKeyboardButton("🗑 حذف دبیر", callback_data="adm_teacher_remove"),
            InlineKeyboardButton("📋 لیست دبیران", callback_data="adm_teacher_list"),
        ],
        [
            InlineKeyboardButton("🔁 اتصال به درس", callback_data="adm_teacher_connect"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_staff_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("☎️ پشتیبان‌ها", callback_data="adm_support_section"),
            InlineKeyboardButton("🧮 حسابدارها", callback_data="adm_accountant_section"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_support_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("➕ افزودن پشتیبان", callback_data="adm_sup_add"),
            InlineKeyboardButton("🗑 حذف پشتیبان", callback_data="adm_sup_remove"),
        ],
        [
            InlineKeyboardButton("📋 لیست پشتیبان‌ها", callback_data="adm_sup_list"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به کادر", callback_data="adm_section_staff"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_accountant_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("➕ افزودن حسابدار", callback_data="adm_acc_add"),
            InlineKeyboardButton("🗑 حذف حسابدار", callback_data="adm_acc_remove"),
        ],
        [
            InlineKeyboardButton("📋 لیست حسابدارها", callback_data="adm_acc_list"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به کادر", callback_data="adm_section_staff"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_finance_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("💳 تراکنش‌ها", callback_data="adm_transactions"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_invoices_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📋 لیست دبیران", callback_data="adm_invoices_list"),
            InlineKeyboardButton("🧹 ریست صورت‌حساب", callback_data="adm_invoices_reset"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_stats_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📊 آمار کامل", callback_data="adm_stats"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_broadcast_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("✉️ همه کاربران", callback_data="adm_bc_all"),
            InlineKeyboardButton("📈 کاربران فعال", callback_data="adm_bc_active"),
        ],
        [
            InlineKeyboardButton("💳 خریداران پکیج", callback_data="adm_bc_buyers"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_access_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("👤 ادمین‌ها", callback_data="adm_admin_section"),
            InlineKeyboardButton("🫅🏻 مالکان", callback_data="adm_owner_section"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_admin_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("➕ افزودن ادمین", callback_data="adm_admin_add"),
            InlineKeyboardButton("🗑 حذف ادمین", callback_data="adm_admin_remove"),
        ],
        [
            InlineKeyboardButton("📋 لیست ادمین‌ها", callback_data="adm_admin_list"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به دسترسی", callback_data="adm_section_access"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_owner_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("➕ افزودن مالک", callback_data="adm_owner_add"),
            InlineKeyboardButton("🗑 حذف مالک", callback_data="adm_owner_remove"),
        ],
        [
            InlineKeyboardButton("📋 لیست مالکان", callback_data="adm_owner_list"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به دسترسی", callback_data="adm_section_access"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_settings_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("👥 جوین اجباری", callback_data="adm_set_force"),
            InlineKeyboardButton("📝 متن‌ها", callback_data="adm_set_texts"),
        ],
        [
            InlineKeyboardButton("💰 تعرفه‌ها", callback_data="adm_set_prices"),
            InlineKeyboardButton("🗂 گروه‌ها", callback_data="adm_set_groups"),
        ],
        [
            InlineKeyboardButton("📚 دروس", callback_data="adm_set_subjects"),
            InlineKeyboardButton("🎛 دکمه‌ها", callback_data="adm_set_buttons"),
        ],
        [
            InlineKeyboardButton("🔧 عملکرد", callback_data="adm_set_performance"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_toggle_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🟢 روشن کردن", callback_data="adm_toggle_on"),
            InlineKeyboardButton("🔴 خاموش کردن", callback_data="adm_toggle_off"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_phones_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📊 تعداد شماره‌ها", callback_data="adm_phones_count"),
        ],
        [
            InlineKeyboardButton("📁 خروجی CSV", callback_data="adm_phones_csv"),
        ],
        [
            InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="adm_back"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_confirm_cancel_buttons(action, id_):
    keyboard = [
        [
            InlineKeyboardButton("✅ تایید", callback_data=f"adm_confirm_{action}_{id_}"),
            InlineKeyboardButton("❌ لغو", callback_data="adm_back"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)