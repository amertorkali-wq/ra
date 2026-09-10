from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import OWNER_ID, DEFAULT_PACKAGES, SUBJECTS
from database import (
    get_stats, get_all_users, get_user, update_user, is_staff,
    add_staff, remove_staff, get_staff_list, get_user_role
)
from keyboards import (
    get_admin_panel_keyboard, get_admin_back_button,
    get_teacher_management_buttons, get_subject_buttons,
    get_staff_management_buttons, get_user_management_buttons
)


# ============================================
# بررسی مالک/ادمین
# ============================================

def is_admin(user_id):
    return user_id == OWNER_ID or is_staff(user_id, role="admin")


def is_owner(user_id):
    return user_id == OWNER_ID


# ============================================
# دستور /admin
# ============================================

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("⛔ شما دسترسی به پنل مدیریت ندارید.")
        return

    await update.message.reply_text(
        "🎛 پنل مدیریت VIOLEX\n\n"
        "لطفاً یک گزینه را انتخاب کنید:",
        reply_markup=get_admin_panel_keyboard()
    )


# ============================================
# دکمه‌های پنل مدیریت
# ============================================

async def handle_admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if not is_admin(user_id):
        await query.answer("⛔ دسترسی ندارید.", show_alert=True)
        return

    # ---- بازگشت ----
    if data == "adm_back":
        await query.edit_message_text(
            "🎛 پنل مدیریت VIOLEX\n\n"
            "لطفاً یک گزینه را انتخاب کنید:",
            reply_markup=get_admin_panel_keyboard()
        )

    # ---- آمار ----
    elif data == "adm_stats":
        stats = get_stats()
        text = (
            f"📊 آمار کلی کاربران\n\n"
            f"👥 کل کاربران: {stats['total_users']}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📝 آمار سوالات\n\n"
            f"❓ مجموع سوالات: {stats['total_questions']}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📚 تفکیک درسی سوالات\n\n"
            f"🧬 زیست‌شناسی: {stats['bio']}\n"
            f"🧪 شیمی: {stats['chem']}\n"
            f"⚡ فیزیک: {stats['phys']}\n"
            f"📐 ریاضی: {stats['math']}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🟩 وضعیت سوالات\n\n"
            f"✅ پاسخ داده شده: {stats['answered']}\n"
            f"⏳ در انتظار پاسخ: {stats['waiting']}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💰 گزارش مالی\n\n"
            f"💵 کل درآمد: {stats['income']:,} تومان"
        )
        await query.edit_message_text(
            text,
            reply_markup=get_admin_back_button()
        )

    # ---- مدیریت دبیران ----
    elif data == "adm_manage_teachers":
        await query.edit_message_text(
            "👨‍🏫 مدیریت دبیران\n\nلطفاً یک گزینه را انتخاب کنید:",
            reply_markup=get_teacher_management_buttons()
        )

    # ---- لیست دبیران ----
    elif data == "adm_teacher_list":
        teachers = get_staff_list("teacher")
        if not teachers:
            text = "📋 هیچ دبیری ثبت نشده است."
        else:
            text = "📋 لیست دبیران:\n\n"
            for i, (tid, subj) in enumerate(teachers, 1):
                text += f"{i}. 🆔 {tid} - درس: {subj or 'نامشخص'}\n"
        await query.edit_message_text(text, reply_markup=get_teacher_management_buttons())

    # ---- افزودن دبیر ----
    elif data == "adm_teacher_add":
        await query.edit_message_text(
            "➕ افزودن دبیر\n\n"
            "لطفاً آیدی عددی دبیر را ارسال کنید.\n\n"
            "⚠️ دبیر باید ابتدا ربات را استارت کرده باشد.",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_teacher_id'

    # ---- حذف دبیر ----
    elif data == "adm_teacher_remove":
        await query.edit_message_text(
            "🗑 حذف دبیر\n\n"
            "لطفاً آیدی عددی دبیر را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_remove_teacher_id'

    # ---- اتصال دبیر به درس ----
    elif data == "adm_teacher_connect":
        await query.edit_message_text(
            "🔁 اتصال دبیر به درس\n\n"
            "لطفاً آیدی عددی دبیر را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_connect_teacher_id'

    # ---- مدیریت ادمین ----
    elif data == "adm_manage_admins":
        await query.edit_message_text(
            "👤 مدیریت ادمین‌ها\n\n"
            "لطفاً یکی از گزینه‌ها را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ افزودن ادمین", callback_data="adm_admin_add")],
                [InlineKeyboardButton("🗑 حذف ادمین", callback_data="adm_admin_remove")],
                [InlineKeyboardButton("📄 لیست ادمین‌ها", callback_data="adm_admin_list")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="adm_back")],
            ])
        )

    elif data == "adm_admin_list":
        admins = get_staff_list("admin")
        if not admins:
            text = "📋 هیچ ادمینی ثبت نشده است."
        else:
            text = "📋 لیست ادمین‌ها:\n\n"
            for i, (aid, _) in enumerate(admins, 1):
                text += f"{i}. 🆔 {aid}\n"
        await query.edit_message_text(text, reply_markup=get_admin_back_button())

    elif data == "adm_admin_add":
        if not is_owner(user_id):
            await query.answer("⛔ فقط مالک می‌تواند ادمین اضافه کند.", show_alert=True)
            return
        await query.edit_message_text(
            "➕ افزودن ادمین\n\n"
            "لطفاً آیدی عددی ادمین را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_admin_id'

    elif data == "adm_admin_remove":
        if not is_owner(user_id):
            await query.answer("⛔ فقط مالک می‌تواند ادمین حذف کند.", show_alert=True)
            return
        await query.edit_message_text(
            "🗑 حذف ادمین\n\n"
            "لطفاً آیدی عددی ادمین را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_remove_admin_id'

    # ---- مدیریت کادر ----
    elif data == "adm_manage_staff":
        await query.edit_message_text(
            "🧑🏻‍💻 مدیریت کادر\n\n"
            "لطفاً یکی از گزینه‌ها را انتخاب کنید:",
            reply_markup=get_staff_management_buttons()
        )

    elif data == "adm_support_manage":
        await query.edit_message_text(
            "☎️ مدیریت پشتیبان‌ها\n\n"
            "لطفاً یکی از گزینه‌ها را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ افزودن پشتیبان", callback_data="adm_sup_add")],
                [InlineKeyboardButton("🗑 حذف پشتیبان", callback_data="adm_sup_remove")],
                [InlineKeyboardButton("📄 لیست پشتیبان‌ها", callback_data="adm_sup_list")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="adm_back")],
            ])
        )

    elif data == "adm_sup_list":
        sups = get_staff_list("support")
        if not sups:
            text = "📋 هیچ پشتیبانی ثبت نشده است."
        else:
            text = "📋 لیست پشتیبان‌ها:\n\n"
            for i, (sid, _) in enumerate(sups, 1):
                text += f"{i}. 🆔 {sid}\n"
        await query.edit_message_text(text, reply_markup=get_admin_back_button())

    elif data == "adm_sup_add":
        if not is_owner(user_id):
            await query.answer("⛔ فقط مالک.", show_alert=True)
            return
        await query.edit_message_text(
            "➕ افزودن پشتیبان\n\n"
            "لطفاً آیدی عددی پشتیبان را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_support_id'

    elif data == "adm_sup_remove":
        if not is_owner(user_id):
            await query.answer("⛔ فقط مالک.", show_alert=True)
            return
        await query.edit_message_text(
            "🗑 حذف پشتیبان\n\n"
            "لطفاً آیدی عددی پشتیبان را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_remove_support_id'

    elif data == "adm_accountant_manage":
        await query.edit_message_text(
            "🧮 مدیریت حسابدارها\n\n"
            "لطفاً یکی از گزینه‌ها را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ افزودن حسابدار", callback_data="adm_acc_add")],
                [InlineKeyboardButton("🗑 حذف حسابدار", callback_data="adm_acc_remove")],
                [InlineKeyboardButton("📄 لیست حسابدارها", callback_data="adm_acc_list")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="adm_back")],
            ])
        )

    elif data == "adm_acc_list":
        accs = get_staff_list("accountant")
        if not accs:
            text = "📋 هیچ حسابداری ثبت نشده است."
        else:
            text = "📋 لیست حسابدارها:\n\n"
            for i, (aid, _) in enumerate(accs, 1):
                text += f"{i}. 🆔 {aid}\n"
        await query.edit_message_text(text, reply_markup=get_admin_back_button())

    elif data == "adm_acc_add":
        if not is_owner(user_id):
            await query.answer("⛔ فقط مالک.", show_alert=True)
            return
        await query.edit_message_text(
            "➕ افزودن حسابدار\n\n"
            "لطفاً آیدی عددی حسابدار را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_accountant_id'

    elif data == "adm_acc_remove":
        if not is_owner(user_id):
            await query.answer("⛔ فقط مالک.", show_alert=True)
            return
        await query.edit_message_text(
            "🗑 حذف حسابدار\n\n"
            "لطفاً آیدی عددی حسابدار را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_remove_accountant_id'

    # ---- مدیریت کاربران ----
    elif data == "adm_manage_users":
        await query.edit_message_text(
            "👫 مدیریت کاربران\n\n"
            "لطفاً یکی از گزینه‌ها را انتخاب کنید:",
            reply_markup=get_user_management_buttons()
        )

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
        if not is_owner(user_id) and not is_admin(user_id):
            await query.answer("⛔ دسترسی ندارید.", show_alert=True)
            return
        await query.edit_message_text(
            "🎁 ارسال هدیه\n\n"
            "لطفاً آیدی عددی کاربر را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_gift_user_id'

    # ---- پیام همگانی ----
    elif data == "adm_broadcast":
        await query.edit_message_text(
            "📣 پیام همگانی\n\n"
            "لطفاً متن پیام خود را ارسال کنید:",
            reply_markup=get_admin_back_button()
        )
        context.user_data['adm_state'] = 'awaiting_broadcast'

    # ---- تنظیمات ----
    elif data == "adm_settings":
        await query.edit_message_text(
            "⚙️ تنظیمات ربات\n\n"
            "لطفاً یکی از گزینه‌ها را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👥 جوین اجباری", callback_data="adm_set_force")],
                [InlineKeyboardButton("📝 مدیریت متن‌ها", callback_data="adm_set_texts")],
                [InlineKeyboardButton("💰 مدیریت تعرفه‌ها", callback_data="adm_set_prices")],
                [InlineKeyboardButton("🗂 مدیریت گروه‌ها", callback_data="adm_set_groups")],
                [InlineKeyboardButton("📚 مدیریت دروس", callback_data="adm_set_subjects")],
                [InlineKeyboardButton("🎛 مدیریت دکمه‌ها", callback_data="adm_set_buttons")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="adm_back")],
            ])
        )

    # ---- هدیه ----
    elif data == "adm_gift":
        if not is_admin(user_id):
            await query.answer("⛔ دسترسی ندارید.", show_alert=True)
            return
        await query.edit_message_text(
            "🎁 هدیه\n\n"
            "لطفاً یکی از گزینه‌ها را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎁 اهدا پکیج به کاربر", callback_data="adm_gift_package")],
                [InlineKeyboardButton("⏰ اهدا مدت زمان به کاربر", callback_data="adm_gift_time")],
                [InlineKeyboardButton("❓ اهدا سوال اضافه به کاربر", callback_data="adm_gift_question")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="adm_back")],
            ])
        )

    # ---- روشن/خاموش ----
    elif data == "adm_toggle":
        if not is_owner(user_id):
            await query.answer("⛔ فقط مالک.", show_alert=True)
            return
        await query.edit_message_text(
            "🚫 روشن/خاموش کردن ربات\n\n"
            "لطفاً یکی از گزینه‌ها را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🟢 روشن کردن ربات", callback_data="adm_toggle_on")],
                [InlineKeyboardButton("🔴 خاموش کردن ربات", callback_data="adm_toggle_off")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="adm_back")],
            ])
        )

    # ---- سایر دکمه‌های تنظیمات (فقط نمایش) ----
    elif data.startswith("adm_set_") or data.startswith("adm_gift_"):
        await query.answer("🚧 این بخش در حال ساخت است.", show_alert=True)


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

    # ---- افزودن ادمین ----
    elif state == 'awaiting_admin_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        aid = int(text)
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

    # ---- افزودن پشتیبان ----
    elif state == 'awaiting_support_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        sid = int(text)
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
                f"کیف پول: {user_data[5]:,} تومان\n"
                f"سوالات باقی: {user_data[6]}\n"
                f"سوالات استفاده‌شده: {user_data[7]}\n"
                f"پکیج فعال: {user_data[8]}\n"
                f"زیرمجموعه: {user_data[10]}\n"
                f"مسدود: {'✅ بله' if user_data[13] else '❌ خیر'}"
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
            new_status = 0 if user_data[13] else 1
            update_user(uid, is_blocked=new_status)
            status_text = "مسدود شد ✅" if new_status else "رفع مسدود شد ✅"
            await update.message.reply_text(f"✅ کاربر {uid} {status_text}")
        context.user_data.pop('adm_state', None)

    # ---- ارسال هدیه ----
    elif state == 'awaiting_gift_user_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        uid = int(text)
        context.user_data['gift_user_id'] = uid
        await update.message.reply_text(
            "🎁 لطفاً مبلغ هدیه (به تومان) را وارد کنید:"
        )
        context.user_data['adm_state'] = 'awaiting_gift_amount'

    elif state == 'awaiting_gift_amount':
        if not text.isdigit():
            await update.message.reply_text("⚠️ مبلغ باید عددی باشد.")
            return True
        amount = int(text)
        uid = context.user_data.get('gift_user_id')
        user_data = get_user(uid)
        if user_data:
            new_wallet = user_data[5] + amount
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

    # ---- پیام همگانی ----
    elif state == 'awaiting_broadcast':
        users = get_all_users()
        success = 0
        for uid in users:
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text=f"📣 پیام همگانی\n\n{text}"
                )
                success += 1
            except:
                pass
        await update.message.reply_text(
            f"✅ پیام به {success} کاربر از {len(users)} ارسال شد."
        )
        context.user_data.pop('adm_state', None)

    else:
        return False

    return True