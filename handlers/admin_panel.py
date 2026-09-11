from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import ContextTypes

from config import OWNER_ID, DEFAULT_PACKAGES, SUBJECTS
from database import (
    get_stats, get_all_users, get_user, update_user, is_staff,
    add_staff, remove_staff, get_staff_list, get_user_role,
    get_shamsi_now, get_shamsi_date, get_shamsi_future_date,
    get_staff_user, staff_exists, get_all_owners, count_owners,
    get_users_stats, get_questions_stats, get_income_stats,
    get_teachers_invoice, reset_teacher_invoice,
    get_user_purchases, get_active_users, get_package_buyers,
)
from keyboards import (
    get_admin_main_keyboard,
    get_admin_back_button,
    get_admin_users_keyboard,
    get_admin_gift_keyboard,
    get_admin_teachers_keyboard,
    get_admin_staff_keyboard,
    get_admin_support_keyboard,
    get_admin_accountant_keyboard,
    get_admin_finance_keyboard,
    get_admin_invoices_keyboard,
    get_admin_stats_keyboard,
    get_admin_broadcast_keyboard,
    get_admin_access_keyboard,
    get_admin_admin_keyboard,
    get_admin_owner_keyboard,
    get_admin_settings_keyboard,
    get_admin_toggle_keyboard,
    get_confirm_cancel_buttons,
)


# آیدی‌های مالک
OWNER_IDS = [7803165903, 7795617350]


def is_admin(user_id):
    return user_id in OWNER_IDS or is_staff(user_id, role="admin") or is_staff(user_id, role="owner")


def is_owner(user_id):
    return user_id in OWNER_IDS


# ============================================
# دستور /admin
# ============================================

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("⛔ شما دسترسی به پنل مدیریت ندارید.")
        return

    # پیام حذف کیبورد معمولی
    try:
        msg = await update.message.reply_text(
            "🔄 در حال بارگذاری...",
            reply_markup=ReplyKeyboardRemove()
        )
        await msg.delete()
    except:
        pass

    # فقط پنل اصلی
    await update.message.reply_text(
        "🏠 پنل مدیریت",
        reply_markup=get_admin_main_keyboard()
    )


# ============================================
# هندلر دکمه‌های پنل مدیریت
# ============================================

async def handle_admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if not is_admin(user_id):
        await query.answer("⛔ دسترسی ندارید.", show_alert=True)
        return

    # ============================================
    # بازگشت به پنل
    # ============================================
    if data == "adm_back":
        try:
            await query.edit_message_text(
                "🏠 پنل مدیریت",
                reply_markup=get_admin_main_keyboard()
            )
        except:
            pass

    # ============================================
    # 👥 بخش کاربران
    # ============================================
    elif data == "adm_section_users":
        try:
            await query.edit_message_text(
                "👥 مدیریت کاربران",
                reply_markup=get_admin_users_keyboard()
            )
        except:
            pass

    elif data == "adm_user_search":
        await query.edit_message_text(
            "🔍 جستجوی کاربر\n\n"
            "لطفاً آیدی عددی کاربر را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_search_user_id'

    elif data == "adm_user_block":
        await query.edit_message_text(
            "🚫 مسدود / رفع مسدود\n\n"
            "لطفاً آیدی عددی کاربر را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_block_user_id'

    elif data == "adm_user_gift":
        await query.edit_message_text(
            "🎁 ارسال هدیه به کاربر\n\n"
            "لطفاً آیدی عددی کاربر را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_gift_user_id'

    elif data == "adm_user_purchases":
        await query.edit_message_text(
            "💳 مشاهده خریدها\n\n"
            "لطفاً آیدی عددی کاربر را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_purchases_user_id'

    # ============================================
    # 🎁 بخش هدایا
    # ============================================
    elif data == "adm_section_gift":
        try:
            await query.edit_message_text(
                "🎁 هدایا",
                reply_markup=get_admin_gift_keyboard()
            )
        except:
            pass

    elif data == "adm_gift_package":
        await query.edit_message_text(
            "🎁 اهدای پکیج\n\n"
            "لطفاً آیدی عددی کاربر را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_gift_package_user_id'

    elif data == "adm_gift_time":
        await query.edit_message_text(
            "⏰ اهدای مدت زمان\n\n"
            "لطفاً آیدی عددی کاربر را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_gift_time_user_id'

    elif data == "adm_gift_question":
        await query.edit_message_text(
            "❓ اهدای سوال\n\n"
            "لطفاً آیدی عددی کاربر را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_gift_question_user_id'

    # ============================================
    # 👨‍🏫 بخش دبیران
    # ============================================
    elif data == "adm_section_teachers":
        try:
            await query.edit_message_text(
                "👨‍🏫 مدیریت دبیران",
                reply_markup=get_admin_teachers_keyboard()
            )
        except:
            pass

    elif data == "adm_teacher_list":
        teachers = get_staff_list("teacher")
        if not teachers:
            text = "📋 هیچ دبیری ثبت نشده است."
        else:
            text = "📋 لیست دبیران:\n\n"
            for i, (tid, uname, subj) in enumerate(teachers, 1):
                text += f"{i}. 🆔 {tid} - @{uname or 'ندارد'} - درس: {subj or 'نامشخص'}\n"
        try:
            await query.edit_message_text(text, reply_markup=get_admin_teachers_keyboard())
        except:
            pass

    elif data == "adm_teacher_add":
        await query.edit_message_text(
            "➕ افزودن دبیر\n\n"
            "لطفاً آیدی عددی دبیر را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_teacher_id'

    elif data == "adm_teacher_remove":
        await query.edit_message_text(
            "🗑 حذف دبیر\n\n"
            "لطفاً آیدی عددی دبیر را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_remove_teacher_id'

    elif data == "adm_teacher_connect":
        await query.edit_message_text(
            "🔁 اتصال دبیر به درس\n\n"
            "لطفاً آیدی عددی دبیر را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_connect_teacher_id'

    elif data == "adm_teacher_edit":
        await query.edit_message_text(
            "📝 ویرایش اطلاعات دبیر\n\n"
            "لطفاً آیدی عددی دبیر را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_edit_teacher_id'

    # ============================================
    # 🧑🏻‍💻 بخش کادر
    # ============================================
    elif data == "adm_section_staff":
        try:
            await query.edit_message_text(
                "🧑🏻‍💻 مدیریت کادر",
                reply_markup=get_admin_staff_keyboard()
            )
        except:
            pass

    elif data == "adm_support_section":
        try:
            await query.edit_message_text(
                "☎️ مدیریت پشتیبان‌ها",
                reply_markup=get_admin_support_keyboard()
            )
        except:
            pass

    elif data == "adm_sup_list":
        sups = get_staff_list("support")
        if not sups:
            text = "📋 هیچ پشتیبانی ثبت نشده است."
        else:
            text = "📋 لیست پشتیبان‌ها:\n\n"
            for i, (sid, uname, _) in enumerate(sups, 1):
                text += f"{i}. 🆔 {sid} - @{uname or 'ندارد'}\n"
        try:
            await query.edit_message_text(text, reply_markup=get_admin_support_keyboard())
        except:
            pass

    elif data == "adm_sup_add":
        await query.edit_message_text(
            "➕ افزودن پشتیبان\n\n"
            "لطفاً آیدی عددی پشتیبان را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_support_id'

    elif data == "adm_sup_remove":
        await query.edit_message_text(
            "🗑 حذف پشتیبان\n\n"
            "لطفاً آیدی عددی پشتیبان را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_remove_support_id'

    elif data == "adm_accountant_section":
        try:
            await query.edit_message_text(
                "🧮 مدیریت حسابدارها",
                reply_markup=get_admin_accountant_keyboard()
            )
        except:
            pass

    elif data == "adm_acc_list":
        accs = get_staff_list("accountant")
        if not accs:
            text = "📋 هیچ حسابداری ثبت نشده است."
        else:
            text = "📋 لیست حسابدارها:\n\n"
            for i, (aid, uname, _) in enumerate(accs, 1):
                text += f"{i}. 🆔 {aid} - @{uname or 'ندارد'}\n"
        try:
            await query.edit_message_text(text, reply_markup=get_admin_accountant_keyboard())
        except:
            pass

    elif data == "adm_acc_add":
        await query.edit_message_text(
            "➕ افزودن حسابدار\n\n"
            "لطفاً آیدی عددی حسابدار را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_accountant_id'

    elif data == "adm_acc_remove":
        await query.edit_message_text(
            "🗑 حذف حسابدار\n\n"
            "لطفاً آیدی عددی حسابدار را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_remove_accountant_id'

    # ============================================
    # 💰 بخش امور مالی
    # ============================================
    elif data == "adm_section_finance":
        try:
            await query.edit_message_text(
                "💰 امور مالی",
                reply_markup=get_admin_finance_keyboard()
            )
        except:
            pass

    elif data == "adm_transactions":
        await query.edit_message_text(
            "💳 تراکنش‌ها\n\n"
            "برای مشاهده تراکنش‌های یک کاربر خاص، آیدی عددی او را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_transactions_user_id'

    # ============================================
    # 🧾 بخش صورت‌حساب
    # ============================================
    elif data == "adm_section_invoices":
        try:
            await query.edit_message_text(
                "🧾 صورت‌حساب‌ها",
                reply_markup=get_admin_invoices_keyboard()
            )
        except:
            pass

    elif data == "adm_invoices_list":
        teachers = get_teachers_invoice()
        if not teachers:
            text = "📋 هیچ دبیری ثبت نشده است."
        else:
            text = "🧾 صورت‌حساب دبیران:\n\n"
            for t in teachers:
                text += (
                    f"👨‍🏫 دبیر: @{t['username'] or 'ندارد'}\n"
                    f"🆔 آیدی: {t['teacher_id']}\n"
                    f"📚 درس: {t['subject'] or 'نامشخص'}\n"
                    f"🎁 سوالات پکیج استارت: {t['start_questions']}\n"
                    f"📦 سوالات پکیج‌های عادی: {t['normal_questions']}\n"
                    f"✅ مجموع: {t['total_questions']}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                )
        try:
            await query.edit_message_text(text, reply_markup=get_admin_invoices_keyboard())
        except:
            pass

    elif data == "adm_invoices_reset":
        if not is_owner(user_id):
            await query.answer("⛔ فقط مالک.", show_alert=True)
            return
        await query.edit_message_text(
            "⚠️ آیا از ریست صورت‌حساب مطمئن هستید؟",
            reply_markup=get_confirm_cancel_buttons("reset_invoice", "all")
        )

    elif data.startswith("adm_confirm_reset_invoice_"):
        reset_teacher_invoice()
        await query.edit_message_text(
            "✅ صورت‌حساب با موفقیت ریست شد.",
            reply_markup=get_admin_invoices_keyboard()
        )

    # ============================================
    # 📊 بخش آمار
    # ============================================
    elif data == "adm_section_stats":
        try:
            await query.edit_message_text(
                "📊 آمار و گزارش‌ها",
                reply_markup=get_admin_stats_keyboard()
            )
        except:
            pass

    elif data == "adm_stats":
        users_stats = get_users_stats()
        q_stats = get_questions_stats()
        income = get_income_stats()

        text = (
            f"📊 آمار کلی کاربران\n\n"
            f"👥 کل کاربران: {users_stats['total']}\n"
            f"📅 امروز: {users_stats['today']}\n"
            f"📅 این هفته: {users_stats['week']}\n"
            f"📅 این ماه: {users_stats['month']}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📝 آمار سوالات\n\n"
            f"❓ مجموع سوالات: {q_stats['total']}\n"
            f"📅 امروز: {q_stats['today']}\n"
            f"📅 این هفته: {q_stats['week']}\n"
            f"📅 این ماه: {q_stats['month']}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📚 تفکیک درسی\n\n"
            f"🧬 زیست: {q_stats['bio']}\n"
            f"🧪 شیمی: {q_stats['chem']}\n"
            f"⚡ فیزیک: {q_stats['phys']}\n"
            f"📐 ریاضی: {q_stats['math']}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🟩 وضعیت سوالات\n\n"
            f"✅ پاسخ داده شده: {q_stats['answered']}\n"
            f"⏳ در انتظار: {q_stats['waiting']}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💰 گزارش مالی\n\n"
            f"💵 درآمد امروز: {income['today']:,} تومان\n"
            f"📅 این هفته: {income['week']:,} تومان\n"
            f"📅 این ماه: {income['month']:,} تومان"
        )
        try:
            await query.edit_message_text(text, reply_markup=get_admin_stats_keyboard())
        except:
            pass

    # ============================================
    # 📢 بخش پیام همگانی
    # ============================================
    elif data == "adm_section_broadcast":
        try:
            await query.edit_message_text(
                "📢 پیام همگانی",
                reply_markup=get_admin_broadcast_keyboard()
            )
        except:
            pass

    elif data in ("adm_bc_all", "adm_bc_active", "adm_bc_buyers"):
        bc_type = "all"
        bc_label = "همه کاربران"
        if data == "adm_bc_active":
            bc_type = "active"
            bc_label = "کاربران فعال"
        elif data == "adm_bc_buyers":
            bc_type = "buyers"
            bc_label = "خریداران پکیج"
        
        await query.edit_message_text(
            f"📢 ارسال به {bc_label}\n\n"
            "لطفاً متن پیام خود را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_broadcast'
        context.user_data['broadcast_type'] = bc_type

    # ============================================
    # 🛡 بخش دسترسی
    # ============================================
    elif data == "adm_section_access":
        try:
            await query.edit_message_text(
                "🛡 مدیریت دسترسی",
                reply_markup=get_admin_access_keyboard()
            )
        except:
            pass

    elif data == "adm_admin_section":
        if not is_owner(user_id):
            await query.answer("⛔ فقط مالک.", show_alert=True)
            return
        try:
            await query.edit_message_text(
                "👤 مدیریت ادمین‌ها",
                reply_markup=get_admin_admin_keyboard()
            )
        except:
            pass

    elif data == "adm_admin_list":
        admins = get_staff_list("admin")
        text = "📋 لیست ادمین‌ها:\n\n"
        text += f"👑 مالک اصلی: {OWNER_ID}\n"
        text += f"👑 مالک دوم: 7795617350\n\n"
        if admins:
            for i, (aid, uname, _) in enumerate(admins, 1):
                text += f"{i}. 🆔 {aid} - @{uname or 'ندارد'}\n"
        else:
            text += "❌ ادمین دیگری ثبت نشده است."
        try:
            await query.edit_message_text(text, reply_markup=get_admin_admin_keyboard())
        except:
            pass

    elif data == "adm_admin_add":
        if not is_owner(user_id):
            await query.answer("⛔ فقط مالک.", show_alert=True)
            return
        await query.edit_message_text(
            "➕ افزودن ادمین\n\n"
            "لطفاً آیدی عددی ادمین را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_admin_id'

    elif data == "adm_admin_remove":
        if not is_owner(user_id):
            await query.answer("⛔ فقط مالک.", show_alert=True)
            return
        await query.edit_message_text(
            "🗑 حذف ادمین\n\n"
            "لطفاً آیدی عددی ادمین را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_remove_admin_id'

    elif data == "adm_owner_section":
        if not is_owner(user_id):
            await query.answer("⛔ فقط مالک.", show_alert=True)
            return
        try:
            await query.edit_message_text(
                "🫅🏻 مدیریت مالک",
                reply_markup=get_admin_owner_keyboard()
            )
        except:
            pass

    elif data == "adm_owner_list":
        owners = get_all_owners()
        text = "📋 لیست مالکان:\n\n"
        text += f"1. 🆔 {OWNER_ID} (مالک اصلی)\n"
        text += f"2. 🆔 7795617350 (مالک دوم)\n"
        for i, oid in enumerate(owners, 3):
            if oid not in OWNER_IDS:
                text += f"{i}. 🆔 {oid}\n"
        try:
            await query.edit_message_text(text, reply_markup=get_admin_owner_keyboard())
        except:
            pass

    elif data == "adm_owner_add":
        if not is_owner(user_id):
            await query.answer("⛔ فقط مالک.", show_alert=True)
            return
        await query.edit_message_text(
            "➕ افزودن مالک\n\n"
            "لطفاً آیدی عددی مالک را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_owner_id'

    elif data == "adm_owner_remove":
        if not is_owner(user_id):
            await query.answer("⛔ فقط مالک.", show_alert=True)
            return
        await query.edit_message_text(
            "🗑 حذف مالک\n\n"
            "لطفاً آیدی عددی مالک را ارسال کنید:\n\n"
            "⚠️ توجه: مالک اصلی و مالک دوم قابل حذف نیستند.",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_remove_owner_id'

    # ============================================
    # ⚙️ بخش تنظیمات
    # ============================================
    elif data == "adm_section_settings":
        if not is_owner(user_id):
            await query.answer("⛔ فقط مالک.", show_alert=True)
            return
        try:
            await query.edit_message_text(
                "⚙️ تنظیمات ربات",
                reply_markup=get_admin_settings_keyboard()
            )
        except:
            pass

    elif data.startswith("adm_set_"):
        await query.answer("🚧 این بخش در حال ساخت است.", show_alert=True)

    # ============================================
    # 🔴 بخش وضعیت ربات
    # ============================================
    elif data == "adm_section_toggle":
        if not is_owner(user_id):
            await query.answer("⛔ فقط مالک.", show_alert=True)
            return
        try:
            await query.edit_message_text(
                "🔴 وضعیت ربات",
                reply_markup=get_admin_toggle_keyboard()
            )
        except:
            pass

    elif data == "adm_toggle_on":
        await query.answer("✅ ربات روشن است.")
        try:
            await query.edit_message_text(
                "🟢 ربات روشن است.",
                reply_markup=get_admin_toggle_keyboard()
            )
        except:
            pass

    elif data == "adm_toggle_off":
        await query.answer("⚠️ این قابلیت موقتاً غیرفعال است.", show_alert=True)

    else:
        await query.answer("⚠️ این دکمه فعال نیست.", show_alert=False)


# ============================================
# دریافت ورودی‌های پنل مدیریت
# ============================================

async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get('adm_state')
    if not state:
        return False

    user_id = update.effective_user.id
    if not is_admin(user_id):
        return False

    text = update.message.text

    # ---- افزودن دبیر ----
    if state == 'awaiting_teacher_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        tid = int(text)
        if staff_exists(tid, "teacher"):
            await update.message.reply_text(f"⚠️ دبیر {tid} قبلاً ثبت شده است.")
        else:
            add_staff(tid, "teacher", added_by=user_id)
            await update.message.reply_text(f"✅ دبیر {tid} اضافه شد.")
        context.user_data.pop('adm_state', None)

    # ---- حذف دبیر ----
    elif state == 'awaiting_remove_teacher_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        tid = int(text)
        remove_staff(tid, role="teacher")
        await update.message.reply_text(f"✅ دبیر {tid} حذف شد.")
        context.user_data.pop('adm_state', None)

    # ---- اتصال دبیر به درس ----
    elif state == 'awaiting_connect_teacher_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        tid = int(text)
        context.user_data['connect_teacher_id'] = tid
        await update.message.reply_text(
            "📚 لطفاً نام درس را وارد کنید:\n"
            "زیست / شیمی / فیزیک / ریاضی"
        )
        context.user_data['adm_state'] = 'awaiting_connect_teacher_subject'

    elif state == 'awaiting_connect_teacher_subject':
        tid = context.user_data.get('connect_teacher_id')
        subject = text
        if subject not in SUBJECTS:
            await update.message.reply_text("⚠️ درس نامعتبر است.")
            return True
        conn = None
        try:
            from database import get_connection
            conn = get_connection()
            c = conn.cursor()
            c.execute("UPDATE staff SET subject = %s WHERE user_id = %s AND role = 'teacher'", (subject, tid))
            conn.commit()
            c.close()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if conn:
                conn.close()
        await update.message.reply_text(f"✅ دبیر {tid} به درس {subject} متصل شد.")
        context.user_data.pop('adm_state', None)
        context.user_data.pop('connect_teacher_id', None)

    # ---- ویرایش دبیر ----
    elif state == 'awaiting_edit_teacher_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        tid = int(text)
        context.user_data['edit_teacher_id'] = tid
        await update.message.reply_text(
            "📝 لطفاً نام درس جدید را وارد کنید:\n"
            "زیست / شیمی / فیزیک / ریاضی"
        )
        context.user_data['adm_state'] = 'awaiting_edit_teacher_subject'

    elif state == 'awaiting_edit_teacher_subject':
        tid = context.user_data.get('edit_teacher_id')
        subject = text
        if subject not in SUBJECTS:
            await update.message.reply_text("⚠️ درس نامعتبر است.")
            return True
        conn = None
        try:
            from database import get_connection
            conn = get_connection()
            c = conn.cursor()
            c.execute("UPDATE staff SET subject = %s WHERE user_id = %s AND role = 'teacher'", (subject, tid))
            conn.commit()
            c.close()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if conn:
                conn.close()
        await update.message.reply_text(f"✅ اطلاعات دبیر {tid} ویرایش شد.")
        context.user_data.pop('adm_state', None)
        context.user_data.pop('edit_teacher_id', None)

    # ---- افزودن ادمین ----
    elif state == 'awaiting_admin_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        aid = int(text)
        if staff_exists(aid, "admin"):
            await update.message.reply_text(f"⚠️ ادمین {aid} قبلاً ثبت شده است.")
        else:
            add_staff(aid, "admin", added_by=user_id)
            await update.message.reply_text(f"✅ ادمین {aid} اضافه شد.")
        context.user_data.pop('adm_state', None)

    # ---- حذف ادمین ----
    elif state == 'awaiting_remove_admin_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        aid = int(text)
        remove_staff(aid, role="admin")
        await update.message.reply_text(f"✅ ادمین {aid} حذف شد.")
        context.user_data.pop('adm_state', None)

    # ---- افزودن مالک ----
    elif state == 'awaiting_owner_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        oid = int(text)
        if staff_exists(oid, "owner"):
            await update.message.reply_text(f"⚠️ مالک {oid} قبلاً ثبت شده است.")
        else:
            add_staff(oid, "owner", added_by=user_id)
            await update.message.reply_text(f"✅ مالک {oid} اضافه شد.")
        context.user_data.pop('adm_state', None)

    # ---- حذف مالک ----
    elif state == 'awaiting_remove_owner_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        oid = int(text)
        if oid in OWNER_IDS:
            await update.message.reply_text("⛔ مالک اصلی و مالک دوم قابل حذف نیستند.")
        elif count_owners() <= 2:
            await update.message.reply_text("⛔ حداقل باید ۲ مالک باقی بماند.")
        else:
            remove_staff(oid, role="owner")
            await update.message.reply_text(f"✅ مالک {oid} حذف شد.")
        context.user_data.pop('adm_state', None)

    # ---- افزودن پشتیبان ----
    elif state == 'awaiting_support_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        sid = int(text)
        if staff_exists(sid, "support"):
            await update.message.reply_text(f"⚠️ پشتیبان {sid} قبلاً ثبت شده است.")
        else:
            add_staff(sid, "support", added_by=user_id)
            await update.message.reply_text(f"✅ پشتیبان {sid} اضافه شد.")
        context.user_data.pop('adm_state', None)

    # ---- حذف پشتیبان ----
    elif state == 'awaiting_remove_support_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        sid = int(text)
        remove_staff(sid, role="support")
        await update.message.reply_text(f"✅ پشتیبان {sid} حذف شد.")
        context.user_data.pop('adm_state', None)

    # ---- افزودن حسابدار ----
    elif state == 'awaiting_accountant_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        aid = int(text)
        if staff_exists(aid, "accountant"):
            await update.message.reply_text(f"⚠️ حسابدار {aid} قبلاً ثبت شده است.")
        else:
            add_staff(aid, "accountant", added_by=user_id)
            await update.message.reply_text(f"✅ حسابدار {aid} اضافه شد.")
        context.user_data.pop('adm_state', None)

    # ---- حذف حسابدار ----
    elif state == 'awaiting_remove_accountant_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        aid = int(text)
        remove_staff(aid, role="accountant")
        await update.message.reply_text(f"✅ حسابدار {aid} حذف شد.")
        context.user_data.pop('adm_state', None)

    # ---- جستجوی کاربر ----
    elif state == 'awaiting_search_user_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        uid = int(text)
        user_data = get_user(uid)
        if not user_data:
            await update.message.reply_text("⚠️ کاربر یافت نشد.")
        else:
            await update.message.reply_text(
                f"👤 اطلاعات کاربر {uid}\n\n"
                f"نام: {user_data[2] or ''} {user_data[3] or ''}\n"
                f"یوزرنیم: @{user_data[1] or 'ندارد'}\n"
                f"شماره: {user_data[4] or 'ندارد'}\n"
                f"کیف پول: {user_data[7]:,} تومان\n"
                f"سوالات باقی: {user_data[8]}\n"
                f"سوالات استفاده‌شده: {user_data[9]}\n"
                f"پکیج فعال: {user_data[10]}\n"
                f"زیرمجموعه: {user_data[12]}\n"
                f"مسدود: {'✅ بله' if user_data[16] else '❌ خیر'}"
            )
        context.user_data.pop('adm_state', None)

    # ---- مسدود/رفع مسدود ----
    elif state == 'awaiting_block_user_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        uid = int(text)
        user_data = get_user(uid)
        if not user_data:
            await update.message.reply_text("⚠️ کاربر یافت نشد.")
        else:
            new_status = 0 if user_data[16] else 1
            update_user(uid, is_blocked=new_status)
            status_text = "مسدود شد ✅" if new_status else "رفع مسدود شد ✅"
            await update.message.reply_text(f"✅ کاربر {uid} {status_text}")
        context.user_data.pop('adm_state', None)

    # ---- مشاهده خریدها ----
    elif state == 'awaiting_purchases_user_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        uid = int(text)
        purchases = get_user_purchases(uid)
        if not purchases:
            await update.message.reply_text(f"📋 هیچ خریدی برای کاربر {uid} ثبت نشده است.")
        else:
            text_out = f"💳 خریدهای کاربر {uid}:\n\n"
            for p in purchases:
                text_out += (
                    f"🆔 {p[0]}\n"
                    f"💰 {p[1]:,} تومان\n"
                    f"📦 نوع: {p[2]}\n"
                    f"📊 وضعیت: {p[3]}\n"
                    f"🕐 {p[4]}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                )
            await update.message.reply_text(text_out)
        context.user_data.pop('adm_state', None)

    # ---- تراکنش‌های کاربر ----
    elif state == 'awaiting_transactions_user_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        uid = int(text)
        purchases = get_user_purchases(uid)
        if not purchases:
            await update.message.reply_text(f"📋 هیچ تراکنشی برای کاربر {uid} ثبت نشده است.")
        else:
            text_out = f"💳 تراکنش‌های کاربر {uid}:\n\n"
            for p in purchases:
                text_out += (
                    f"🆔 {p[0]}\n"
                    f"💰 {p[1]:,} تومان\n"
                    f"📦 {p[2]}\n"
                    f"📊 {p[3]}\n"
                    f"🕐 {p[4]}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                )
            await update.message.reply_text(text_out)
        context.user_data.pop('adm_state', None)

    # ---- ارسال هدیه پول ----
    elif state == 'awaiting_gift_user_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        uid = int(text)
        context.user_data['gift_user_id'] = uid
        await update.message.reply_text("🎁 لطفاً مبلغ هدیه (به تومان) را وارد کنید:")
        context.user_data['adm_state'] = 'awaiting_gift_amount'

    elif state == 'awaiting_gift_amount':
        if not text.isdigit():
            await update.message.reply_text("⚠️ مبلغ باید عددی باشد.")
            return True
        amount = int(text)
        uid = context.user_data.get('gift_user_id')
        user_data = get_user(uid)
        if user_data:
            new_wallet = user_data[7] + amount
            update_user(uid, wallet=new_wallet)
            await update.message.reply_text(f"✅ {amount:,} تومان به کاربر {uid} هدیه داده شد.")
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text=f"🎁 هدیه {amount:,} تومانی به کیف پول شما اضافه شد."
                )
            except:
                pass
        context.user_data.pop('adm_state', None)
        context.user_data.pop('gift_user_id', None)

    # ---- اهدای پکیج ----
    elif state == 'awaiting_gift_package_user_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        uid = int(text)
        context.user_data['gift_package_user_id'] = uid
        await update.message.reply_text(
            "📦 لطفاً نام پکیج رو وارد کنید:\n\n"
            "مثال: پکیج 1 ماهه"
        )
        context.user_data['adm_state'] = 'awaiting_gift_package_name'

    elif state == 'awaiting_gift_package_name':
        pkg_name = text
        uid = context.user_data.get('gift_package_user_id')
        user_data = get_user(uid)
        if user_data:
            update_user(uid, active_package=pkg_name)
            await update.message.reply_text(f"✅ پکیج {pkg_name} به کاربر {uid} هدیه داده شد.")
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text=f"🎁 پکیج {pkg_name} به شما هدیه داده شد!"
                )
            except:
                pass
        context.user_data.pop('adm_state', None)
        context.user_data.pop('gift_package_user_id', None)

    # ---- اهدای مدت زمان ----
    elif state == 'awaiting_gift_time_user_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        uid = int(text)
        context.user_data['gift_time_user_id'] = uid
        await update.message.reply_text("⏰ لطفاً تعداد روزهای هدیه رو وارد کنید:")
        context.user_data['adm_state'] = 'awaiting_gift_time_days'

    elif state == 'awaiting_gift_time_days':
        if not text.isdigit():
            await update.message.reply_text("⚠️ تعداد روز باید عددی باشد.")
            return True
        days = int(text)
        uid = context.user_data.get('gift_time_user_id')
        new_expire = get_shamsi_future_date(days)
        user_data = get_user(uid)
        if user_data:
            update_user(uid, package_expire_date=new_expire)
            await update.message.reply_text(f"✅ {days} روز به اعتبار کاربر {uid} اضافه شد.")
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text=f"🎁 {days} روز به اعتبار شما اضافه شد!\n⏳ اعتبار جدید تا: {new_expire}"
                )
            except:
                pass
        context.user_data.pop('adm_state', None)
        context.user_data.pop('gift_time_user_id', None)

    # ---- اهدای سوال ----
    elif state == 'awaiting_gift_question_user_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        uid = int(text)
        context.user_data['gift_question_user_id'] = uid
        await update.message.reply_text("❓ لطفاً تعداد سوالات هدیه رو وارد کنید:")
        context.user_data['adm_state'] = 'awaiting_gift_question_count'

    elif state == 'awaiting_gift_question_count':
        if not text.isdigit():
            await update.message.reply_text("⚠️ تعداد باید عددی باشد.")
            return True
        count = int(text)
        uid = context.user_data.get('gift_question_user_id')
        user_data = get_user(uid)
        if user_data:
            new_questions = user_data[8] + count
            update_user(uid, questions_remaining=new_questions)
            await update.message.reply_text(f"✅ {count} سوال به کاربر {uid} هدیه داده شد.")
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text=f"🎁 {count} سوال به حساب شما اضافه شد!"
                )
            except:
                pass
        context.user_data.pop('adm_state', None)
        context.user_data.pop('gift_question_user_id', None)

    # ---- پیام همگانی ----
    elif state == 'awaiting_broadcast':
        bc_type = context.user_data.get('broadcast_type', 'all')
        
        if bc_type == 'all':
            users = get_all_users()
        elif bc_type == 'active':
            users = get_active_users(30)
        elif bc_type == 'buyers':
            users = get_package_buyers()
        else:
            users = get_all_users()
        
        success = 0
        failed = 0
        for uid in users:
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text=f"📣 پیام همگانی\n\n{text}"
                )
                success += 1
            except:
                failed += 1
        
        await update.message.reply_text(
            f"✅ نتیجه ارسال:\n\n"
            f"📨 موفق: {success}\n"
            f"❌ ناموفق: {failed}\n"
            f"👥 کل: {len(users)}"
        )
        context.user_data.pop('adm_state', None)
        context.user_data.pop('broadcast_type', None)

    else:
        return False

    return True