from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import (
    get_ticket, reply_ticket, close_ticket, is_staff,
    get_open_ticket_for_support, take_ticket
)
from texts import SUPPORT_ANSWER_REQUEST, SUPPORT_BUSY, SUPPORT_REPLY_INSTRUCTION


def is_support(user_id):
    return (
        is_staff(user_id, role="support") or
        is_staff(user_id, role="admin") or
        is_staff(user_id, role="owner")
    )


# ============================================
# دکمه "پاسخ دادن" توسط پشتیبان
# ============================================

async def support_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    user_id = query.from_user.id
    username = query.from_user.username or query.from_user.first_name or "پشتیبان"
    ticket_id = int(query.data.split("_")[2])

    if not is_support(user_id):
        await query.answer("⛔ شما پشتیبان نیستید.", show_alert=True)
        return

    # بررسی صف: آیا پشتیبان تیکت باز دارد؟
    open_ticket = get_open_ticket_for_support(user_id)
    if open_ticket and open_ticket != ticket_id:
        await query.answer(
            "⚠️ شما در حال پاسخ به یک تیکت دیگر هستید. ابتدا آن را ببندید.",
            show_alert=True
        )
        return

    ticket = get_ticket(ticket_id)
    if not ticket:
        await query.answer("⚠️ تیکت یافت نشد.", show_alert=True)
        return

    # بررسی وضعیت تیکت
    if ticket[4] not in ('waiting', 'taken'):
        await query.answer("⚠️ این تیکت قبلاً بسته شده است.", show_alert=True)
        return

    # اگر قبلاً توسط پشتیبان دیگری برداشته شده
    if ticket[4] == 'taken' and ticket[5] != user_id:
        await query.answer("⚠️ این تیکت قبلاً توسط پشتیبان دیگری برداشته شده است.", show_alert=True)
        return

    await query.answer("✅ تیکت به شما تخصیص داده شد.")

    # ثبت در دیتابیس
    take_ticket(ticket_id, user_id, username)

    # ویرایش پیام اصلی
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("بستن ❌", callback_data=f"sup_close_{ticket_id}")]
            ])
        )
    except:
        pass

    # پیام راهنما به پشتیبان (ریپلای)
    reply_msg = await query.message.reply_text(
        SUPPORT_ANSWER_REQUEST.format(code=ticket[2], username=username),
        parse_mode="Markdown"
    )

    # ذخیره message_id برای بررسی ریپلای
    context.user_data['active_ticket_id'] = ticket_id
    context.user_data['active_ticket_message_id'] = reply_msg.message_id


# ============================================
# دریافت پاسخ پشتیبان (با ریپلای)
# ============================================

async def support_send_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ticket_id = context.user_data.get('active_ticket_id')
    reply_to_msg_id = context.user_data.get('active_ticket_message_id')

    if not ticket_id or not is_support(user_id):
        return False

    # بررسی ریپلای
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "⚠️ *لطفاً پاسخ خود را به صورت ریپلای روی پیام راهنما ارسال کنید.*\n\n"
            "روی پیام راهنمای پشتیبانی ریپلای بزنید و پاسخ را بنویسید.",
            parse_mode="Markdown"
        )
        return True

    if update.message.reply_to_message.message_id != reply_to_msg_id:
        await update.message.reply_text(
            "⚠️ *لطفاً پاسخ خود را به صورت ریپلای روی پیام راهنما ارسال کنید.*",
            parse_mode="Markdown"
        )
        return True

    ticket = get_ticket(ticket_id)
    if not ticket:
        return True

    student_id = ticket[1]
    text = update.message.text

    # ثبت پاسخ
    reply_ticket(ticket_id, text)

    # ارسال به کاربر
    try:
        await context.bot.send_message(
            chat_id=student_id,
            text=(
                f"💬 *پاسخ پشتیبانی*\n\n"
                f"🆔 کد پیگیری: `{ticket[2]}`\n"
                f"🕐 زمان: {'{now}'}\n\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"{text}"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Error sending to user: {e}")

    await update.message.reply_text(
        f"✅ *پاسخ شما به کاربر ارسال شد.*\n\n"
        f"🆔 کد پیگیری: `{ticket[2]}`\n\n"
        f"اکنون می‌توانید تیکت را ببندید.",
        parse_mode="Markdown"
    )

    return True


# ============================================
# بستن تیکت توسط پشتیبان
# ============================================

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

    close_ticket(ticket_id)

    # پاک کردن active_ticket_id
    if context.user_data.get('active_ticket_id') == ticket_id:
        context.user_data.pop('active_ticket_id', None)
        context.user_data.pop('active_ticket_message_id', None)

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except:
        pass

    await query.message.reply_text(
        f"✅ *تیکت {ticket[2]} بسته شد.*",
        parse_mode="Markdown"
    )

    # اطلاع به کاربر
    try:
        await context.bot.send_message(
            chat_id=ticket[1],
            text=(
                f"✅ *تیکت شما بسته شد.*\n\n"
                f"🆔 کد پیگیری: `{ticket[2]}`\n\n"
                f"از اینکه با ویولکس همراه هستید سپاسگزاریم. 🌟"
            ),
            parse_mode="Markdown"
        )
    except:
        pass