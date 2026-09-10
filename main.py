from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

from config import TOKEN, TEACHER_TIMEOUT_MINUTES, SUPPORT_TIMEOUT_HOURS
from database import init_db
from keyboards import get_main_menu_keyboard

from handlers import user_panel, teacher_panel, support_panel
from handlers import accountant_panel, admin_panel


async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if await admin_panel.handle_admin_input(update, context):
            return
    except Exception as e:
        print(f"Admin error: {e}")

    try:
        if await accountant_panel.handle_card_reject_reason(update, context):
            return
    except Exception as e:
        print(f"Accountant error: {e}")

    try:
        if await teacher_panel.handle_followup(update, context):
            return
    except Exception as e:
        print(f"Teacher error: {e}")

    if context.user_data.get('active_ticket_id'):
        user_id = update.effective_user.id
        if support_panel.is_support(user_id):
            if await support_panel.support_send_reply(update, context):
                return

    if context.user_data.get('active_question_id'):
        user_id = update.effective_user.id
        if teacher_panel.is_teacher(user_id):
            await teacher_panel.teacher_send_answer(update, context)
            return

    await user_panel.handle_message(update, context)


async def photo_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('active_ticket_id'):
        user_id = update.effective_user.id
        if support_panel.is_support(user_id):
            if await support_panel.support_send_reply(update, context):
                return

    if context.user_data.get('active_question_id'):
        user_id = update.effective_user.id
        if teacher_panel.is_teacher(user_id):
            await teacher_panel.teacher_send_answer(update, context)
            return

    await user_panel.handle_photo(update, context)


async def contact_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await user_panel.handle_contact(update, context)


async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data or ""

    if data == "check_sub":
        await user_panel.check_subscription(update, context)
        return

    if data.startswith("adm_"):
        await admin_panel.handle_admin_buttons(update, context)
        return

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

    if data.startswith("t_answer_"):
        await teacher_panel.teacher_answer(update, context)
        return
    if data.startswith("t_close_"):
        await teacher_panel.teacher_close(update, context)
        return

    if data.startswith("s_understood_"):
        await teacher_panel.student_understood(update, context)
        return
    if data.startswith("s_followup_"):
        await teacher_panel.student_followup(update, context)
        return

    if data.startswith("sup_answer_"):
        await support_panel.support_answer(update, context)
        return
    if data.startswith("sup_close_"):
        await support_panel.support_close(update, context)
        return

    if data.startswith("user_continue_"):
        await support_panel.user_continue_ticket(update, context)
        return
    if data.startswith("user_close_"):
        await support_panel.user_close_ticket(update, context)
        return
    if data == "cancel_ticket_msg":
        context.user_data.pop('in_ticket', None)
        await query.answer("❌ لغو شد.")
        try:
            await query.message.delete()
        except:
            pass
        return

    if data in ("about_biology", "about_chemistry", "about_physics", "about_math"):
        await teacher_panel.show_teacher_bio(update, context)
        return
    if data == "about_back":
        await teacher_panel.back_to_about(update, context)
        return

    if data in ("auth", "card_list", "add_card", "remove_card") or data.startswith("del_card_"):
        await user_panel.handle_auth_buttons(update, context)
        return

    if data in ("buy_package", "buy_question", "back_to_main", "back_to_balance",
                "pay_wallet", "pay_gateway", "paid_check", "back_to_packages"):
        await user_panel.handle_balance_buttons(update, context)
        return

    if data.startswith("buy_pkg_") or data.startswith("pay_card_"):
        await user_panel.handle_balance_buttons(update, context)
        return

    # لغو احراز هویت
    if data == "cancel_auth":
        context.user_data.pop('awaiting_auth_code', None)
        context.user_data.pop('awaiting_auth_phone', None)
        context.user_data.pop('awaiting_card_photo', None)
        context.user_data.pop('awaiting_card_number', None)
        context.user_data.pop('card_photo', None)

        await query.answer("✅ احراز هویت لغو شد.")
        try:
            await query.message.delete()
        except:
            pass
        await query.message.reply_text(
            "❌ *احراز هویت لغو شد.*\n\n"
            "می‌توانید از منوی اصلی دوباره اقدام کنید.",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    await query.answer("⚠️ این دکمه فعال نیست.", show_alert=False)


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await admin_panel.admin_command(update, context)


def main():
    print("🔵 در حال راه‌اندازی دیتابیس PostgreSQL...")
    init_db()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", user_panel.start))
    app.add_handler(CommandHandler("admin", admin_command))

    app.add_handler(CallbackQueryHandler(callback_router))
    app.add_handler(MessageHandler(filters.CONTACT, contact_router))
    app.add_handler(MessageHandler(filters.PHOTO, photo_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_router))

    job_queue = app.job_queue

    job_queue.run_repeating(
        teacher_panel.check_teacher_timeouts,
        interval=300,
        first=60
    )

    job_queue.run_repeating(
        support_panel.check_support_timeouts,
        interval=1800,
        first=120
    )

    print("✅ ربات VIOLEX با موفقیت راه‌اندازی شد!")
    print(f"⏰ تایم لیمیت دبیران: {TEACHER_TIMEOUT_MINUTES} دقیقه")
    print(f"⏰ تایم لیمیت پشتیبانی: {SUPPORT_TIMEOUT_HOURS} ساعت")
    print("💾 دیتابیس: PostgreSQL (دائمی)")
    print("🚀 در حال اجرا...")

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()