from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

from config import TOKEN
from database import init_db

from handlers import user_panel, teacher_panel, support_panel
from handlers import accountant_panel, admin_panel


# ============================================
# هندلرهای عمومی (غیر از پنل‌های خاص)
# ============================================

async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مسیریاب پیام‌های متنی"""

    # 1) پنل مدیریت (اگر در حالت انتظار ورودی باشد)
    if await admin_panel.handle_admin_input(update, context):
        return

    # 2) پنل حسابداری (دلیل رد کارت)
    if await accountant_panel.handle_card_reject_reason(update, context):
        return

    # 3) پنل دبیران (سوال تکمیلی)
    if await teacher_panel.handle_followup(update, context):
        return

    # 4) پنل پشتیبانی (اگر در حالت پاسخ باشد)
    if context.user_data.get('active_ticket_id'):
        user_id = update.effective_user.id
        if support_panel.is_support(user_id):
            await support_panel.support_send_reply(update, context)
            return

    # 5) پنل دبیران (اگر در حالت پاسخ باشد)
    if context.user_data.get('active_question_id'):
        user_id = update.effective_user.id
        if teacher_panel.is_teacher(user_id):
            await teacher_panel.teacher_send_answer(update, context)
            return

    # 6) پنل عمومی کاربر
    await user_panel.handle_message(update, context)


async def photo_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مسیریاب پیام‌های عکس"""

    # 1) پنل دبیران (اگر در حالت پاسخ باشد)
    if context.user_data.get('active_question_id'):
        user_id = update.effective_user.id
        if teacher_panel.is_teacher(user_id):
            await teacher_panel.teacher_send_answer(update, context)
            return

    # 2) پنل عمومی
    await user_panel.handle_photo(update, context)


async def contact_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مسیریاب مخاطبین (شماره تلفن)"""
    await user_panel.handle_contact(update, context)


# ============================================
# مسیریاب دکمه‌های شیشه‌ای
# ============================================

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data or ""

    # ---- بررسی عضویت ----
    if data == "check_sub":
        await user_panel.check_subscription(update, context)
        return

    # ---- پنل مدیریت ----
    if data.startswith("adm_"):
        await admin_panel.handle_admin_buttons(update, context)
        return

    # ---- پنل حسابداری ----
    if data.startswith("acc_"):
        if data.startswith("acc_verify_"):
            await accountant_panel.acc_verify_card(update, context)
        elif data.startswith("acc_reject_"):
            await accountant_panel.acc_reject_card(update, context)
        elif data.startswith("acc_tx_ok_"):
            await accountant_panel.acc_verify_transaction(update, context)
        elif data.startswith("acc_tx_no_"):
            await accountant_panel.acc_reject_transaction(update, context)
        return

    # ---- پنل دبیران ----
    if data.startswith("t_answer_"):
        await teacher_panel.teacher_answer(update, context)
        return
    if data.startswith("t_close_"):
        await teacher_panel.teacher_close(update, context)
        return

    # ---- پاسخ دانش‌آموز ----
    if data.startswith("s_understood_"):
        await teacher_panel.student_understood(update, context)
        return
    if data.startswith("s_followup_"):
        await teacher_panel.student_followup(update, context)
        return

    # ---- پنل پشتیبانی ----
    if data.startswith("sup_answer_"):
        await support_panel.support_answer(update, context)
        return
    if data.startswith("sup_close_"):
        await support_panel.support_close(update, context)
        return

    # ---- دکمه‌های درباره ما ----
    if data.startswith("about_"):
        await user_panel.handle_about_buttons(update, context)
        return

    # ---- دکمه‌های احراز هویت ----
    if data in ("auth", "card_list", "add_card", "remove_card") or data.startswith("del_card_"):
        await user_panel.handle_auth_buttons(update, context)
        return

    # ---- دکمه‌های افزایش موجودی ----
    if data in ("buy_package", "buy_question", "back_to_main", "back_to_balance",
                "pay_wallet", "pay_gateway", "paid_check"):
        await user_panel.handle_balance_buttons(update, context)
        return

    if data.startswith("buy_pkg_") or data.startswith("pay_card_"):
        await user_panel.handle_balance_buttons(update, context)
        return

    # ---- پیش‌فرض ----
    await query.answer("⚠️ این دکمه فعال نیست.", show_alert=False)


# ============================================
# دستورات
# ============================================

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await admin_panel.admin_command(update, context)


# ============================================
# تابع اصلی
# ============================================

def main():
    # راه‌اندازی دیتابیس
    init_db()

    # ساخت اپلیکیشن
    app = Application.builder().token(TOKEN).build()

    # ---- هندلرهای دستورات ----
    app.add_handler(CommandHandler("start", user_panel.start))
    app.add_handler(CommandHandler("admin", admin_command))

    # ---- هندلر دکمه‌های شیشه‌ای ----
    app.add_handler(CallbackQueryHandler(callback_router))

    # ---- هندلر مخاطبین ----
    app.add_handler(MessageHandler(filters.CONTACT, contact_router))

    # ---- هندلر عکس‌ها ----
    app.add_handler(MessageHandler(filters.PHOTO, photo_router))

    # ---- هندلر پیام‌های متنی ----
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_router))

    print("✅ ربات VIOLEX با موفقیت راه‌اندازی شد!")
    print("🚀 در حال اجرا...")

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()