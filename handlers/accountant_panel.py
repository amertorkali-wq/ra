from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import (
    get_card, verify_card, is_staff, get_user, update_user
)


# ============================================
# بررسی حسابدار بودن
# ============================================

def is_accountant(user_id):
    return (
        is_staff(user_id, role="accountant") or
        is_staff(user_id, role="admin") or
        is_staff(user_id, role="owner")
    )


# ============================================
# تایید کارت
# ============================================

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
        f"✅ کارت {card[2][-4:]}**** تایید شد.\n"
        f"👤 کاربر: {card[1]}"
    )

    # اطلاع به کاربر
    try:
        await context.bot.send_message(
            chat_id=card[1],
            text=(
                "✅ کارت بانکی شما توسط تیم مالی تایید شد.\n"
                "اکنون می‌توانید از طریق درگاه پرداخت خرید خود را انجام دهید."
            )
        )
    except Exception as e:
        print(f"Error notifying user: {e}")


# ============================================
# رد کارت
# ============================================

async def acc_reject_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    await query.answer("⚠️ لطفاً دلیل رد را ارسال کنید.")

    context.user_data['rejecting_card_id'] = card_id

    await query.message.reply_text(
        "📝 لطفاً دلیل رد کارت را وارد کنید:"
    )


# ============================================
# دریافت دلیل رد کارت
# ============================================

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

    await update.message.reply_text(
        f"❌ کارت {card[2][-4:]}**** رد شد.\n"
        f"📌 دلیل: {reason}"
    )

    # اطلاع به کاربر
    try:
        await context.bot.send_message(
            chat_id=card[1],
            text=(
                f"❌ کارت بانکی شما تایید نشد.\n\n"
                f"📌 دلیل: {reason}\n\n"
                f"لطفاً کارت دیگری ثبت کنید."
            )
        )
    except Exception as e:
        print(f"Error notifying user: {e}")

    return True


# ============================================
# تایید تراکنش مشکوک
# ============================================

async def acc_verify_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("✅ تراکنش تایید شد.")

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except:
        pass

    await query.message.reply_text("✅ تراکنش تایید شد.")


# ============================================
# رد تراکنش مشکوک
# ============================================

async def acc_reject_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("❌ تراکنش رد شد.")

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except:
        pass

    await query.message.reply_text("❌ تراکنش رد شد.")