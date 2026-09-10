from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import SUPPORT_TIMEOUT_HOURS
from database import (
    get_ticket, reply_ticket, close_ticket, is_staff,
    get_open_ticket_for_support, take_ticket, add_ticket_message,
    get_shamsi_now, get_expired_tickets
)
from texts import (
    SUPPORT_ANSWER_REQUEST, SUPPORT_BUSY, SUPPORT_TICKET_TAKEN,
    SUPPORT_TIMEOUT_MSG
)


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
    full_name = f"{query.from_user.first_name or ''} {query.from_user.last_name or ''}".strip()
    ticket_id = int(query.data.split("_")[2])

    if not is_support(user_id):
        await query.answer("⛔ شما پشتیبان نیستید.", show_alert=True)
        return

    # بررسی صف
    open_ticket = get_open_ticket_for_support(user_id)
    if open_ticket and open_ticket != ticket_id:
        await query.answer(SUPPORT_BUSY, show_alert=True)
        return

    ticket = get_ticket(ticket_id)
    if not ticket:
        await query.answer("⚠️ تیکت یافت نشد.", show_alert=True)
        return

    if ticket[4] not in ('waiting', 'taken'):
        await query.answer("⚠️ این تیکت قبلاً بسته شده است.", show_alert=True)
        return

    if ticket[4] == 'taken' and ticket[5] != user_id:
        await query.answer("⚠️ این تیکت قبلاً توسط پشتیبان دیگری برداشته شده است.", show_alert=True)
        return

    await query.answer("✅ تیکت به شما تخصیص داده شد.")

    take_ticket(ticket_id, user_id, username, full_name or username)

    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ بستن", callback_data=f"sup_close_{ticket_id}")]
            ])
        )
    except:
        pass

    # پیام راهنما
    reply_msg = await query.message.reply_text(
        SUPPORT_ANSWER_REQUEST.format(code=ticket[2], username=username),
        parse_mode="Markdown"
    )

    context.user_data['active_ticket_id'] = ticket_id
    context.user_data['active_ticket_message_id'] = reply_msg.message_id

    await query.message.reply_text(
        SUPPORT_TICKET_TAKEN.format(code=ticket[2]),
        parse_mode="Markdown"
    )


# ============================================
# دریافت پاسخ پشتیبان (فقط با ریپلای)
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
                f"🕐 زمان: {get_shamsi_now()}\n\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"{text}"
            ),
            parse_mode="Markdown"
        )

        # پیام دکمه‌های ادامه
        from keyboards import get_user_ticket_buttons
        await context.bot.send_message(
            chat_id=student_id,
            text=(
                f"🔄 *آیا مشکل شما حل شد؟*\n\n"
                f"می‌توانید دوباره صحبت کنید یا تیکت را ببندید."
            ),
            reply_markup=get_user_ticket_buttons(ticket_id),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Error sending to user: {e}")

    await update.message.reply_text(
        f"✅ *پاسخ شما به کاربر ارسال شد.*\n\n"
        f"🆔 کد پیگیری: `{ticket[2]}`\n\n"
        f"اکنون می‌توانید تیکت را ببندید یا منتظر پاسخ کاربر بمانید.",
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

    if context.user_data.get('active_ticket_id') == ticket_id:
        context.user_data.pop('active_ticket_id', None)
        context.user_data.pop('active_ticket_message_id', None)

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except:
        pass

    await query.message.reply_text(
        f"✅ *تیکت* `{ticket[2]}` *بسته شد.*",
        parse_mode="Markdown"
    )

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


# ============================================
# پاسخ کاربر داخل تیکت (ادامه صحبت)
# ============================================

async def user_continue_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    ticket_id = int(query.data.split("_")[2])
    user_id = query.from_user.id

    ticket = get_ticket(ticket_id)
    if not ticket:
        await query.answer("⚠️ تیکت یافت نشد.", show_alert=True)
        return

    if ticket[1] != user_id:
        await query.answer("⛔ این تیکت شما نیست.", show_alert=True)
        return

    if ticket[4] == 'closed':
        await query.answer("⚠️ این تیکت بسته شده است.", show_alert=True)
        return

    context.user_data['in_ticket'] = ticket_id

    await query.message.reply_text(
        "💬 *لطفاً پیام خود را ارسال کنید.*\n\n"
        "می‌توانید متن، عکس یا فایل ارسال کنید.\n\n"
        "برای لغو، روی دکمه زیر بزنید.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ لغو", callback_data="cancel_ticket_msg")]
        ]),
        parse_mode="Markdown"
    )


# ============================================
# دریافت پیام کاربر در تیکت
# ============================================

async def user_send_ticket_message(update: Update, context: ContextTypes.DEFAULT_TYPE, ticket_id: int):
    user = update.effective_user
    user_id = user.id

    ticket = get_ticket(ticket_id)
    if not ticket:
        context.user_data.pop('in_ticket', None)
        await update.message.reply_text("⚠️ تیکت یافت نشد.")
        return

    if ticket[4] == 'closed':
        context.user_data.pop('in_ticket', None)
        await update.message.reply_text("⚠️ این تیکت بسته شده است.")
        return

    # استخراج متن یا فایل
    text = update.message.text or update.message.caption or ""
    file_id = None

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
    elif update.message.document:
        file_id = update.message.document.file_id

    # ذخیره پیام
    add_ticket_message(ticket_id, 'user', user_id, update.message.message_id, text, file_id)

    # ارسال به گروه پشتیبانی
    from config import SUPPORT_GROUP
    try:
        msg_text = (
            f"💬 *پیام جدید در تیکت* `{ticket[2]}`\n\n"
            f"👤 کاربر: @{user.username or 'ندارد'}\n"
            f"🆔 ID: `{user_id}`\n"
            f"🕐 زمان: {get_shamsi_now()}\n\n"
            f"📝 *متن:*\n{text}"
        )

        if file_id:
            try:
                if update.message.photo:
                    await context.bot.send_photo(
                        chat_id=SUPPORT_GROUP,
                        photo=file_id,
                        caption=msg_text,
                        parse_mode="Markdown"
                    )
                else:
                    await context.bot.send_document(
                        chat_id=SUPPORT_GROUP,
                        document=file_id,
                        caption=msg_text,
                        parse_mode="Markdown"
                    )
            except Exception as e:
                print(f"Error sending file to support: {e}")
        else:
            await context.bot.send_message(
                chat_id=SUPPORT_GROUP,
                text=msg_text,
                parse_mode="Markdown"
            )
    except Exception as e:
        print(f"Error sending to support: {e}")

    context.user_data.pop('in_ticket', None)
    await update.message.reply_text(
        "✅ *پیام شما ارسال شد.*\n\n"
        "پشتیبان در اسرع وقت پاسخ خواهد داد.",
        parse_mode="Markdown"
    )


# ============================================
# بستن تیکت توسط کاربر
# ============================================

async def user_close_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    ticket_id = int(query.data.split("_")[2])
    user_id = query.from_user.id

    ticket = get_ticket(ticket_id)
    if not ticket:
        await query.answer("⚠️ تیکت یافت نشد.", show_alert=True)
        return

    if ticket[1] != user_id:
        await query.answer("⛔ این تیکت شما نیست.", show_alert=True)
        return

    close_ticket(ticket_id)

    try:
        await query.edit_message_text(
            f"✅ *تیکت شما بسته شد.*\n\n"
            f"🆔 کد پیگیری: `{ticket[2]}`\n\n"
            f"از اینکه با ویولکس همراه هستید سپاسگزاریم. 🌟",
            parse_mode="Markdown"
        )
    except:
        pass


# ============================================
# بررسی تایم اوت تیکت‌ها (JobQueue)
# ============================================

async def check_support_timeouts(context: ContextTypes.DEFAULT_TYPE):
    """بستن خودکار تیکت‌های منقضی"""
    expired = get_expired_tickets()

    for ticket_id, ticket_code in expired:
        ticket = get_ticket(ticket_id)
        if not ticket:
            continue

        close_ticket(ticket_id)

        # پیام به کاربر
        try:
            await context.bot.send_message(
                chat_id=ticket[1],
                text=(
                    f"⏰ *تیکت شما به صورت خودکار بسته شد.*\n\n"
                    f"🆔 کد پیگیری: `{ticket_code}`\n\n"
                    f"دلیل: عدم پاسخ در ۲۴ ساعت گذشته.\n\n"
                    f"اگر همچنان مشکل دارید، می‌توانید تیکت جدید ثبت کنید."
                ),
                parse_mode="Markdown"
            )
        except:
            pass

        # پیام به پشتیبان
        if ticket[5]:
            try:
                await context.bot.send_message(
                    chat_id=ticket[5],
                    text=SUPPORT_TIMEOUT_MSG.format(code=ticket_code),
                    parse_mode="Markdown"
                )
            except:
                pass