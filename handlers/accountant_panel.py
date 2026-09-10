from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_card, verify_card, is_staff


def is_accountant(user_id):
    return (
        is_staff(user_id, role="accountant") or
        is_staff(user_id, role="admin") or
        is_staff(user_id, role="owner")
    )


async def acc_verify_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    card_id = int(query.data.split("_")[2])

    if not is_accountant(user_id):
        await query.answer("⛔ شما حسابدار نیستید.", show_alert=True)
        return

    card = get_card(card_id)
    if not card:
        await query.answer("⚠️ کارت یافت نشد.", show_alert=True)
        return

    await query.answer("✅ کارت تایید شد.")
    verify_card(card_id, verified=True)

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except:
        pass

    await query.message.reply_text(
        f"✅ کارت {card[2][-4:]}**** تایید شد."
    )

    try:
        await context.bot.send_message(
            chat_id=card[1],
            text="✅ کارت بانکی شما توسط تیم مالی تایید شد.\nاکنون می‌توانید از طریق درگاه پرداخت خرید خود را انجام دهید."
        )
    except:
        pass


async def acc_reject_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    card_id = int(query.data.split("_")[2])

    if not is_accountant(user_id):
        await query.answer("⛔ شما حسابدار نیستید.", show_alert=True)
        return

    await query.answer("⚠️ لطفاً دلیل رد را ارسال کنید.")
    context.user_data['rejecting_card_id'] = card_id

    await query.message.reply_text("📝 لطفاً دلیل رد کارت را وارد کنید:")


async def handle_card_reject_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    card_id = context.user_data.get('rejecting_card_id')
    if not card_id:
        return False

    user_id = update.effective_user.id
    if not is_accountant(user_id):
        return False

    reason = update.message.text
    card = get_card(card_id)
    if not card:
        context.user_data.pop('rejecting_card_id', None)
        return True

    verify_card(card_id, verified=False, reason=reason)
    context.user_data.pop('rejecting_card_id', None)

    await update.message.reply_text(f"❌ کارت رد شد.\n📌 دلیل: {reason}")

    try:
        await context.bot.send_message(
            chat_id=card[1],
            text=f"❌ کارت بانکی شما تایید نشد.\n\n📌 دلیل: {reason}\n\nلطفاً کارت دیگری ثبت کنید."
        )
    except:
        pass

    return True


async def acc_verify_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("✅ تراکنش تایید شد.")
    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except:
        pass


async def acc_reject_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("❌ تراکنش رد شد.")
    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except:
        pass