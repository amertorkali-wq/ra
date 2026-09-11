from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import ContextTypes

from config import OWNER_ID, DEFAULT_PACKAGES, SUBJECTS
from database import (
    get_stats, get_all_users, get_user, update_user, is_staff,
    add_staff, remove_staff, get_staff_list, get_user_role,
    get_shamsi_now, get_shamsi_date, get_shamsi_future_date
)
from keyboards import (
    get_admin_main_keyboard,
    get_admin_users_keyboard,
    get_admin_education_keyboard,
    get_admin_finance_keyboard,
    get_admin_reports_keyboard,
    get_admin_access_keyboard,
    get_admin_settings_keyboard,
    get_admin_toggle_keyboard,
    get_admin_back_button,
    get_teacher_management_buttons,
    get_staff_management_buttons,
    get_user_management_buttons,
    get_subject_buttons,
    get_gift_buttons,
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

    # پاک کردن دکمه‌های کیبورد معمولی
    await update.message.reply_text(
        "🎛 *پنل مدیریت VIOLEX*\n\n"
        "لطفاً یک دسته را انتخاب کنید:",
        reply_markup=ReplyKeyboardRemove()
    )

    await update.message.reply_text(
        "🏠 *پنل اصلی مدیریت*\n\n"
        "دسته مورد نظر خود را انتخاب کنید:",
        reply_markup=get_admin_main_keyboard(),
        parse_mode="Markdown"
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
    # بازگشت به پنل اصلی
    # ============================================
    if data == "adm_back":
        try:
            await query.edit_message_text(
                "🏠 *پنل اصلی مدیریت*\n\n"
                "دسته مورد نظر خود را انتخاب کنید:",
                reply_markup=get_admin_main_keyboard(),
                parse_mode="Markdown"
            )
        except:
            pass

    # ============================================
    # 👥 بخش مدیریت کاربران
    # ============================================
    elif data == "adm_section_users":
        try:
            await query.edit_message_text(
                "👥 *مدیریت کاربران*\n\n"
                "از گزینه‌های زیر انتخاب کنید:",
                reply_markup=get_admin_users_keyboard(),
                parse_mode="Markdown"
            )
        except:
            pass

    elif data == "adm_manage_users":
        try:
            await query.edit_message_text(
                "👥 *مدیریت کاربران*\n\n"
                "لطفاً یکی از گزینه‌ها را انتخاب کنید:",
                reply_markup=get_user_management_buttons(),
                parse_mode="Markdown"
            )
        except:
            pass

    elif data == "adm_user_search":
        await query.edit_message_text(
            "🔍 *جستجوی کاربر*\n\n"
            "لطفاً آیدی عددی کاربر را ارسال کنید:",
            reply_markup=get_admin_back_button(),
            parse_mode="Markdown"
        )
        context.user_data['adm_state'] = 'awaiting_search_user_id'

    elif data == "adm_user_block":
        await query.edit_message_text(
            "🚫 *مسدود / رفع مسدود*\n\n"
            "لطفاً آیدی عددی کاربر را ارسال کنید:",
            reply_markup=get_admin_back_button(),
            parse_mode="Markdown"
        )
        context.user_data['adm_state'] = 'awaiting_block_user_id'

    elif data == "adm_user_gift":
        await query.edit_message_text(
            "🎁 *ارسال هدیه به کاربر*\n\n"
            "لطفاً آیدی عددی کاربر را ارسال کنید:",
            reply_markup=get_admin_back_button(),
            parse_mode="Markdown"
        )
        context.user_data['adm_state'] = 'awaiting_gift_user_id'

    elif data == "adm_user_purchases":
        await query.edit_message_text(
            "💳 *مشاهده خریدها*\n\n"
            "لطفاً آیدی عددی کاربر را ارسال کنید:",
            reply_markup=get_admin_back_button(),
            parse_mode="Markdown"
        )
        context.user_data['adm_state'] = 'awaiting_purchases_user_id'

    # ============================================
    # 👨‍🏫 بخش مدیریت آموزشی
    # ============================================
    elif data == "adm_section_education":
        try:
            await query.edit_message_text(
                "👨‍🏫 *مدیریت آموزشی*\n\n"
                "از گزینه‌های زیر انتخاب کنید:",
                reply_markup=get_admin_education_keyboard(),
                parse_mode="Markdown"
            )
        except:
            pass

    elif data == "adm_manage_teachers":
        try:
            await query.edit_message_text(
                "👨‍🏫 *مدیریت دبیران*\n\n"
                "لطفاً یک گزینه را انتخاب کنید:",
                reply_markup=get_teacher_management_buttons(),
                parse_mode="Markdown"
            )
        except:
            pass

    elif data == "adm_teacher_list":
        teachers = get_staff_list("teacher")
        if not teachers:
            text = "📋 هیچ دبیری ثبت نشده است."
        else:
            text = "📋 *لیست دبیران:*\n\n"
            for i, (tid, uname, subj) in enumerate(teachers, 1):
                text += f"{i}. 🆔 `{tid}` - @{uname or 'ندارد'} - درس: {subj or 'نامشخص'}\n"
        try:
            await query.edit_message_text(text, reply_markup=get_teacher_management_buttons(), parse_mode="Markdown")
        except:
            pass

    elif data == "adm_teacher_add":
        await query.edit_message_text(
            "➕ *افزودن دبیر*\n\n"
            "لطفاً آیدی عددی دبیر را ارسال کنید:",
            reply_markup=get_admin_back_button(),
            parse_mode="Markdown"
        )
        context.user_data['adm_state'] = 'awaiting_teacher_id'

    elif data == "adm_teacher_remove":
        await query.edit_message_text(
            "🗑 *حذف دبیر*\n\n"
            "لطفاً آیدی عددی دبیر را ارسال کنید:",
            reply_markup=get_admin_back_button(),
            parse_mode="Markdown"
        )
        context.user_data['adm_state'] = 'awaiting_remove_teacher_id'

    elif data == "adm_teacher_connect":
        await query.edit_message_text(
            "🔁 *اتصال دبیر به درس*\n\n"
            "لطفاً آیدی عددی دبیر را ارسال کنید:",
            reply_markup=get_admin_back_button(),
            parse_mode="Markdown"
        )
        context.user_data['adm_state'] = 'awaiting_connect_teacher_id'

    elif data == "adm_teacher_edit":
        await query.edit_message_text(
            "📝 *ویرایش اطلاعات دبیر*\n\n"
            "این بخش در حال ساخت است.",
            reply_markup=get_teacher_management_buttons()
        )

    elif data == "adm_manage_staff":
        try:
            await query.edit_message_text(
                "👨‍💼 *مدیریت کادر آموزشی*\n\n"
                "لطفاً یکی از گزینه‌ها را انتخاب کنید:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("☎️ مدیریت پشتیبان‌ها", callback_data="adm_support_manage", style="primary")],
                    [InlineKeyboardButton("🧮 مدیریت حسابدارها", callback_data="adm_accountant_manage", style="success")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="adm_section_education", style="danger")],
                ]),
                parse_mode="Markdown"
            )
        except:
            pass

    elif data == "adm_support_manage":
        try:
            await query.edit_message_text(
                "☎️ *مدیریت پشتیبان‌ها*\n\n"
                "لطفاً یکی از گزینه‌ها را انتخاب کنید:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ افزودن پشتیبان", callback_data="adm_sup_add", style="success")],
                    [InlineKeyboardButton("🗑 حذف پشتیبان", callback_data="adm_sup_remove", style="danger")],
                    [InlineKeyboardButton("📄 لیست پشتیبان‌ها", callback_data="adm_sup_list", style="primary")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="adm_manage_staff", style="danger")],
                ]),
                parse_mode="Markdown"
            )
        except:
            pass

    elif data == "adm_sup_list":
        sups = get_staff_list("support")
        if not sups:
            text = "📋 هیچ پشتیبانی ثبت نشده است."
        else:
            text = "📋 *لیست پشتیبان‌ها:*\n\n"
            for i, (sid, uname, _) in enumerate(sups, 1):
                text += f"{i}. 🆔 `{sid}` - @{uname or 'ندارد'}\n"
        try:
            await query.edit_message_text(text, reply_markup=get_admin_back_button(), parse_mode="Markdown")
        except:
            pass

    elif data == "adm_sup_add":
        await query.edit_message_text(
            "➕ *افزودن پشتیبان*\n\n"
            "لطفاً آیدی عددی پشتیبان را ارسال کنید:",
            reply_markup=get_admin_back_button(),
            parse_mode="Markdown"
        )
        context.user_data['adm_state'] = 'awaiting_support_id'

    elif data == "adm_sup_remove":
        await query.edit_message_text(
            "🗑 *حذف پشتیبان*\n\n"
            "لطفاً آیدی عددی پشتیبان را ارسال کنید:",
            reply_markup=get_admin_back_button(),
            parse_mode="Markdown"
        )
        context.user_data['adm_state'] = 'awaiting_remove_support_id'

    elif data == "adm_accountant_manage":
        try:
            await query.edit_message_text(
                "🧮 *مدیریت حسابدارها*\n\n"
                "لطفاً یکی از گزینه‌ها را انتخاب کنید:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ افزودن حسابدار", callback_data="adm_acc_add", style="success")],
                    [InlineKeyboardButton("🗑 حذف حسابدار", callback_data="adm_acc_remove", style="danger")],
                    [InlineKeyboardButton("📄 لیست حسابدارها", callback_data="adm_acc_list", style="primary")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="adm_manage_staff", style="danger")],
                ]),
                parse_mode="Markdown"
            )
        except:
            pass

    elif data == "adm_acc_list":
        accs = get_staff_list("accountant")
        if not accs:
            text = "📋 هیچ حسابداری ثبت نشده است."
        else:
            text = "📋 *لیست حسابدارها:*\n\n"
            for i, (aid, uname, _) in enumerate(accs, 1):
                text += f"{i}. 🆔 `{aid}` - @{uname or 'ندارد'}\n"
        try:
            await query.edit_message_text(text, reply_markup=get_admin_back_button(), parse_mode="Markdown")
        except:
            pass

    elif data == "adm_acc_add":
        await query.edit_message_text(
            "➕ *افزودن حسابدار*\n\n"
            "لطفاً آیدی عددی حسابدار را ارسال کنید:",
            reply_markup=get_admin_back_button(),
            parse_mode="Markdown"
        )
        context.user_data['adm_state'] = 'awaiting_accountant_id'

    elif data == "adm_acc_remove":
        await query.edit_message_text(
            "🗑 *حذف حسابدار*\n\n"
            "لطفاً آیدی عددی حسابدار را ارسال کنید:",
            reply_markup=get_admin_back_button(),
            parse_mode="Markdown"
        )
        context.user_data['adm_state'] = 'awaiting_remove_accountant_id'

    # ============================================
    # 💰 بخش امور مالی
    # ============================================
    elif data == "adm_section_finance":
        try:
            await query.edit_message_text(
                "💰 *امور مالی*\n\n"
                "از گزینه‌های زیر انتخاب کنید:",
                reply_markup=get_admin_finance_keyboard(),
                parse_mode="Markdown"
            )
        except:
            pass

    elif data == "adm_invoices":
        teachers = get_staff_list("teacher")
        if not teachers:
            text = "📋 هیچ دبیری ثبت نشده است."
            try:
                await query.edit_message_text(text, reply_markup=get_admin_back_button())
            except:
                pass
        else:
            text = "🧾 *صورت‌حساب دبیران:*\n\n"
            for i, (tid, uname, subj) in enumerate(teachers, 1):
                text += (
                    f"👨‍🏫 دبیر: @{uname or 'ندارد'}\n"
                    f"🆔 آیدی: `{tid}`\n"
                    f"📚 درس: {subj or 'نامشخص'}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                )
            try:
                await query.edit_message_text(
                    text,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🧹 ریست صورت‌حساب", callback_data="adm_invoices_reset", style="danger")],
                        [InlineKeyboardButton("🔙 بازگشت", callback_data="adm_section_finance", style="danger")],
                    ]),
                    parse_mode="Markdown"
                )
            except:
                pass

    elif data == "adm_invoices_reset":
        if not is_owner(user_id):
            await query.answer("⛔ فقط مالک.", show_alert=True)
            return
        await query.answer("✅ صورت‌حساب ریست شد.")
        try:
            await query.edit_message_text(
                "✅ *صورت‌حساب با موفقیت ریست شد.*",
                reply_markup=get_admin_back_button(),
                parse_mode="Markdown"
            )
        except:
            pass

    elif data == "adm_transactions":
        await query.edit_message_text(
            "📊 *تراکنش‌ها و پرداخت‌ها*\n\n"
            "این بخش در حال ساخت است.",
            reply_markup=get_admin_back_button()
        )

    # ============================================
    # 📊 بخش آمار و گزارش
    # ============================================
    elif data == "adm_section_reports":
        try:
            await query.edit_message_text(
                "📊 *آمار و گزارش‌ها*\n\n"
                "از گزینه‌های زیر انتخاب کنید:",
                reply_markup=get_admin_reports_keyboard(),
                parse_mode="Markdown"
            )
        except:
            pass

    elif data == "adm_stats":
        stats = get_stats()
        text = (
            f"📊 *آمار کلی کاربران*\n\n"
            f"👥 کل کاربران: {stats['total_users']}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📝 *آمار سوالات*\n\n"
            f"❓ مجموع سوالات: {stats['total_questions']}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📚 *تفکیک درسی سوالات*\n\n"
            f"🧬 زیست‌شناسی: {stats['bio']}\n"
            f"🧪 شیمی: {stats['chem']}\n"
            f"⚡ فیزیک: {stats['phys']}\n"
            f"📐 ریاضی: {stats['math']}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🟩 *وضعیت سوالات*\n\n"
            f"✅ پاسخ داده شده: {stats['answered']}\n"
            f"⏳ در انتظار پاسخ: {stats['waiting']}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💰 *گزارش مالی*\n\n"
            f"💵 کل درآمد: {stats['income']:,} تومان"
        )
        try:
            await query.edit_message_text(text, reply_markup=get_admin_back_button(), parse_mode="Markdown")
        except:
            pass

    # ============================================
    # 📢 بخش ارتباطات - پیام همگانی
    # ============================================
    elif data == "adm_broadcast":
        try:
            await query.edit_message_text(
                "📢 *پیام همگانی*\n\n"
                "لطفاً یکی از گزینه‌ها را انتخاب کنید:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✉️ ارسال به همه کاربران", callback_data="adm_bc_all", style="success")],
                    [InlineKeyboardButton("📈 ارسال به کاربران فعال", callback_data="adm_bc_active", style="primary")],
                    [InlineKeyboardButton("💳 ارسال به خریداران پکیج", callback_data="adm_bc_buyers", style="success")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="adm_back", style="danger")],
                ]),
                parse_mode="Markdown"
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
            f"📢 *ارسال به {bc_label}*\n\n"
            "لطفاً متن پیام خود را ارسال کنید:",
            reply_markup=get_admin_back_button(),
            parse_mode="Markdown"
        )
        context.user_data['adm_state'] = 'awaiting_broadcast'
        context.user_data['broadcast_type'] = bc_type

    # ============================================
    # 🛡 بخش مدیریت دسترسی
    # ============================================
    elif data == "adm_section_access":
        try:
            await query.edit_message_text(
                "🛡 *مدیریت دسترسی*\n\n"
                "از گزینه‌های زیر انتخاب کنید:",
                reply_markup=get_admin_access_keyboard(),
                parse_mode="Markdown"
            )
        except:
            pass

    elif data == "adm_manage_admins":
        if not is_owner(user_id):
            await query.answer("⛔ فقط مالک.", show_alert=True)
            return
        try:
            await query.edit_message_text(
                "👥 *مدیریت ادمین‌ها*\n\n"
                "لطفاً یکی از گزینه‌ها را انتخاب کنید:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ افزودن ادمین", callback_data="adm_admin_add", style="success")],
                    [InlineKeyboardButton("🗑 حذف ادمین", callback_data="adm_admin_remove", style="danger")],
                    [InlineKeyboardButton("📄 لیست ادمین‌ها", callback_data="adm_admin_list", style="primary")],
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="adm_section_access", style="danger")],
                ]),
                parse_mode="Markdown"
            )
        except:
            pass

    elif data == "adm_admin_list":
        admins = get_staff_list("admin")
        text = "📋 *لیست ادمین‌ها:*\n\n"
        text += f"👑 مالک اصلی: `{OWNER_ID}`\n"
        text += f"👑 مالک دوم: `7795617350`\n\n"
        if admins:
            for i, (aid, uname, _) in enumerate(admins, 1):
                text += f"{i}. 🆔 `{aid}` - @{uname or 'ندارد'}\n"
        else:
            text += "❌ ادمین دیگری ثبت نشده است."
        try:
            await query.edit_message_text(text, reply_markup=get_admin_back_button(), parse_mode="Markdown")
        except:
            pass

    elif data == "adm_admin_add":
        if not is_owner(user_id):
            await query.answer("⛔ فقط مالک.", show_alert=True)
            return
        await query.edit_message_text(
            "➕ *افزودن ادمین*\n\n"
            "لطفاً آیدی عددی ادمین را ارسال کنید:",
            reply_markup=get_admin_back_button(),
            parse_mode="Markdown"
        )
        context.user_data['adm_state'] = 'awaiting_admin_id'

    elif data == "adm_admin_remove":
        if not is_owner(user_id):
            await query.answer("⛔ فقط مالک.", show_alert=True)
            return
        await query.edit_message_text(
            "🗑 *حذف ادمین*\n\n"
            "لطفاً آیدی عددی ادمین را ارسال کنید:",
            reply_markup=get_admin_back_button(),
            parse_mode="Markdown"
        )
        context.user_data['adm_state'] = 'awaiting_remove_admin_id'

    elif data == "adm_manage_owners":
        if not is_owner(user_id):
            await query.answer("⛔ فقط مالک.", show_alert=True)
            return
        try:
            await query.edit_message_text(
                "👑 *مالک و دسترسی اصلی*\n\n"
                f"👑 مالک اصلی: `{OWNER_ID}`\n"
                f"👑 مالک دوم: `7795617350`\n\n"
                "⚠️ این بخش فقط برای مشاهده است.",
                reply_markup=get_admin_back_button(),
                parse_mode="Markdown"
            )
        except:
            pass

    # ============================================
    # ⚙️ بخش تنظیمات
    # ============================================
    elif data == "adm_section_settings":
        try:
            await query.edit_message_text(
                "⚙️ *تنظیمات ربات*\n\n"
                "از گزینه‌های زیر انتخاب کنید:",
                reply_markup=get_admin_settings_keyboard(),
                parse_mode="Markdown"
            )
        except:
            pass

    elif data.startswith("adm_set_"):
        await query.answer("🚧 این بخش در حال ساخت است.", show_alert=True)

    # ============================================
    # 🔴 بخش وضعیت ربات
    # ============================================
    elif data == "adm_section_toggle":
        try:
            await query.edit_message_text(
                "🔴 *وضعیت ربات*\n\n"
                "لطفاً یکی از گزینه‌ها را انتخاب کنید:",
                reply_markup=get_admin_toggle_keyboard(),
                parse_mode="Markdown"
            )
        except:
            pass

    elif data == "adm_toggle_on":
        await query.answer("✅ ربات روشن است.")
        try:
            await query.edit_message_text(
                "🟢 *ربات روشن است.*",
                reply_markup=get_admin_back_button(),
                parse_mode="Markdown"
            )
        except:
            pass

    elif data == "adm_toggle_off":
        await query.answer("⚠️ این قابلیت موقتاً غیرفعال است.", show_alert=True)

    # ============================================
    # 🎁 بخش هدایا
    # ============================================
    elif data == "adm_gift":
        try:
            await query.edit_message_text(
                "🎁 *هدایا*\n\n"
                "لطفاً یکی از گزینه‌ها را انتخاب کنید:",
                reply_markup=get_gift_buttons(),
                parse_mode="Markdown"
            )
        except:
            pass

    elif data == "adm_gift_package":
        await query.edit_message_text(
            "🎁 *اهدای پکیج به کاربر*\n\n"
            "لطفاً آیدی عددی کاربر را ارسال کنید:",
            reply_markup=get_admin_back_button(),
            parse_mode="Markdown"
        )
        context.user_data['adm_state'] = 'awaiting_gift_package_user_id'

    elif data == "adm_gift_time":
        await query.edit_message_text(
            "⏰ *اهدای مدت زمان به کاربر*\n\n"
            "لطفاً آیدی عددی کاربر را ارسال کنید:",
            reply_markup=get_admin_back_button(),
            parse_mode="Markdown"
        )
        context.user_data['adm_state'] = 'awaiting_gift_time_user_id'

    elif data == "adm_gift_question":
        await query.edit_message_text(
            "❓ *اهدای سوال اضافه به کاربر*\n\n"
            "لطفاً آیدی عددی کاربر را ارسال کنید:",
            reply_markup=get_admin_back_button(),
            parse_mode="Markdown"
        )
        context.user_data['adm_state'] = 'awaiting_gift_question_user_id'

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
        add_staff(tid, "teacher", added_by=user_id)
        await update.message.reply_text(f"✅ دبیر `{tid}` اضافه شد.", parse_mode="Markdown")
        context.user_data.pop('adm_state', None)

    # ---- حذف دبیر ----
    elif state == 'awaiting_remove_teacher_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        tid = int(text)
        remove_staff(tid, role="teacher")
        await update.message.reply_text(f"✅ دبیر `{tid}` حذف شد.", parse_mode="Markdown")
        context.user_data.pop('adm_state', None)

    # ---- افزودن ادمین ----
    elif state == 'awaiting_admin_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        aid = int(text)
        add_staff(aid, "admin", added_by=user_id)
        await update.message.reply_text(f"✅ ادمین `{aid}` اضافه شد.", parse_mode="Markdown")
        context.user_data.pop('adm_state', None)

    # ---- حذف ادمین ----
    elif state == 'awaiting_remove_admin_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        aid = int(text)
        remove_staff(aid, role="admin")
        await update.message.reply_text(f"✅ ادمین `{aid}` حذف شد.", parse_mode="Markdown")
        context.user_data.pop('adm_state', None)

    # ---- افزودن پشتیبان ----
    elif state == 'awaiting_support_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        sid = int(text)
        add_staff(sid, "support", added_by=user_id)
        await update.message.reply_text(f"✅ پشتیبان `{sid}` اضافه شد.", parse_mode="Markdown")
        context.user_data.pop('adm_state', None)

    # ---- حذف پشتیبان ----
    elif state == 'awaiting_remove_support_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        sid = int(text)
        remove_staff(sid, role="support")
        await update.message.reply_text(f"✅ پشتیبان `{sid}` حذف شد.", parse_mode="Markdown")
        context.user_data.pop('adm_state', None)

    # ---- افزودن حسابدار ----
    elif state == 'awaiting_accountant_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        aid = int(text)
        add_staff(aid, "accountant", added_by=user_id)
        await update.message.reply_text(f"✅ حسابدار `{aid}` اضافه شد.", parse_mode="Markdown")
        context.user_data.pop('adm_state', None)

    # ---- حذف حسابدار ----
    elif state == 'awaiting_remove_accountant_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        aid = int(text)
        remove_staff(aid, role="accountant")
        await update.message.reply_text(f"✅ حسابدار `{aid}` حذف شد.", parse_mode="Markdown")
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
                f"👤 *اطلاعات کاربر* `{uid}`\n\n"
                f"نام: {user_data[2] or ''} {user_data[3] or ''}\n"
                f"یوزرنیم: @{user_data[1] or 'ندارد'}\n"
                f"شماره: `{user_data[4] or 'ندارد'}`\n"
                f"کیف پول: {user_data[7]:,} تومان\n"
                f"سوالات باقی: {user_data[8]}\n"
                f"سوالات استفاده‌شده: {user_data[9]}\n"
                f"پکیج فعال: {user_data[10]}\n"
                f"زیرمجموعه: {user_data[12]}\n"
                f"مسدود: {'✅ بله' if user_data[16] else '❌ خیر'}",
                parse_mode="Markdown"
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
            await update.message.reply_text(f"✅ کاربر `{uid}` {status_text}", parse_mode="Markdown")
        context.user_data.pop('adm_state', None)

    # ---- مشاهده خریدها ----
    elif state == 'awaiting_purchases_user_id':
        if not text.isdigit():
            await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
            return True
        uid = int(text)
        await update.message.reply_text(
            f"💳 *خریدهای کاربر* `{uid}`\n\n"
            f"برای مشاهده جزئیات، به دیتابیس مراجعه کنید.",
            parse_mode="Markdown"
        )
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
            await update.message.reply_text(f"✅ {amount:,} تومان به کاربر `{uid}` هدیه داده شد.", parse_mode="Markdown")
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text=f"🎁 *هدیه {amount:,} تومانی به کیف پول شما اضافه شد.*",
                    parse_mode="Markdown"
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
            await update.message.reply_text(f"✅ پکیج `{pkg_name}` به کاربر `{uid}` هدیه داده شد.", parse_mode="Markdown")
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text=f"🎁 *پکیج {pkg_name} به شما هدیه داده شد!*",
                    parse_mode="Markdown"
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
            await update.message.reply_text(f"✅ {days} روز به اعتبار کاربر `{uid}` اضافه شد.", parse_mode="Markdown")
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text=f"🎁 *{days} روز به اعتبار شما اضافه شد!*\n⏳ اعتبار جدید تا: {new_expire}",
                    parse_mode="Markdown"
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
            await update.message.reply_text(f"✅ {count} سوال به کاربر `{uid}` هدیه داده شد.", parse_mode="Markdown")
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text=f"🎁 *{count} سوال به حساب شما اضافه شد!*",
                    parse_mode="Markdown"
                )
            except:
                pass
        context.user_data.pop('adm_state', None)
        context.user_data.pop('gift_question_user_id', None)

    # ---- پیام همگانی ----
    elif state == 'awaiting_broadcast':
        users = get_all_users()
        success = 0
        for uid in users:
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text=f"📣 *پیام همگانی*\n\n{text}",
                    parse_mode="Markdown"
                )
                success += 1
            except:
                pass
        await update.message.reply_text(
            f"✅ پیام به {success} کاربر از {len(users)} ارسال شد."
        )
        context.user_data.pop('adm_state', None)
        context.user_data.pop('broadcast_type', None)

    else:
        return False

    return True