from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_ticket, reply_ticket, is_staff
from texts import SUPPORT_ANSWER_REQUEST, SUPPORT_BUSY


def is_support(user_id):
    return (
        is_staff(user_id, role="support") or
        is_staff(user_id, role="admin") or
        is_staff(user_id, role="owner")
    )


async def support_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    user_id = query.from_user.id
    ticket_id = int(query.data.split("_")[2])

    if not is_support(user_id):
        await query.answer("⛔ شما پشتیبان نیستید.", show_alert=True)
        return

    ticket = get_ticket(ticket_id)
    if not ticket:
        await query.answer("⚠️ تیکت یافت نشد.", show_alert=True)
        return

    active_id = context.user_data.get('active_ticket_id')
    if active_id and active_id != ticket_id:
        await query.answer(SUPPORT_BUSY, show_alert=True)
        return

    await query.answer("✅ تیکت به شما تخصیص داده شد.")

    context.user_data['active_ticket_id'] = ticket_id

    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("بستن ❌", callback_data=f"sup_close_{ticket_id}")]
            ])
        )
    except:
        pass

    await query.message.reply_text(
        SUPPORT_ANSWER_REQUEST.format(code=ticket[2])
    )


async def support_send_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ticket_id = context.user_data.get('active_ticket_id')

    if not ticket_id or not is_support(user_id):
        return

    ticket = get_ticket(ticket_id)
    if not ticket:
        return

    student_id = ticket[1]
    text = update.message.text

    reply_ticket(ticket_id, text)

    try:
        await context.bot.send_message(
            chat_id=student_id,
            text=(
                f"💬 پاسخ پشتیبانی\n\n"
                f"🆔 کد پیگیری: {ticket[2]}\n\n"
                f"{text}"
            )
        )
    except Exception as e:
        print(f"Error sending to user: {e}")

    await update.message.reply_text(
        f"✅ پاسخ شما به کاربر ارسال شد.\n\n"
        f"🆔 کد پیگیری: {ticket[2]}"
    )


async def support_close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    user_id = query.from_user.id
    ticket_id = int(query.data.split("_")[2])

    if not is_support(user_id):
        await query.answer("⛔ شما پشتیبان نیستید.", show_alert=True)
        return

    ticket = get_ticket(ticket_id)
    if not ticket:
        await query.answer("⚠️ تیکت یافت نشد.", show_alert=True)
        return

    await query.answer("✅ تیکت بسته شد.")

    if context.user_data.get('active_ticket_id') == ticket_id:
        context.user_data.pop('active_ticket_id', None)

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except:
        pass

    await query.message.reply_text(
        f"✅ تیکت {ticket[2]} بسته شد."
    )