from datetime import datetime, timedelta
import jdatetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes

from config import SUBJECTS, TEACHER_TIMEOUT_MINUTES, ABOUT_IMAGE_URL
from database import (
    get_question, update_question, is_staff, get_user, get_shamsi_now,
    get_teacher_active_question, get_expired_questions
)
from keyboards import (
    get_teacher_close_button, get_student_answer_buttons,
    get_teacher_navigation_buttons, get_about_buttons
)
from texts import (
    TEACHER_ANSWER_REQUEST, TEACHER_BUSY, TEACHER_TAKEN_MSG,
    TEACHER_TIMEOUT_MSG, QUESTION_TAKEN_BY_OTHER, ABOUT_US_TEXT,
    TEACHERS_INFO
)


def is_teacher(user_id):
    return (
        is_staff(user_id, role="teacher") or
        is_staff(user_id, role="owner") or
        is_staff(user_id, role="admin")
    )


# ============================================
# دبیران - پاسخ به سوال
# ============================================

async def teacher_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username or query.from_user.first_name or "دبیر"
    full_name = f"{query.from_user.first_name or ''} {query.from_user.last_name or ''}".strip()
    data = query.data
    question_id = int(data.split("_")[2])

    if not is_teacher(user_id):
        await query.answer("⛔ شما دبیر نیستید.", show_alert=True)
        return

    active = get_teacher_active_question(user_id)
    if active and active[0] != question_id:
        await query.answer(TEACHER_BUSY, show_alert=True)
        return

    question = get_question(question_id)
    if not question:
        await query.answer("⚠️ سؤال یافت نشد.", show_alert=True)
        return

    if question[7] not in ('waiting', 'taken'):
        await query.answer("⚠️ این سؤال قبلاً بسته شده است.", show_alert=True)
        return

    if question[7] == 'taken' and question[8] != user_id:
        teacher_name = question[10] or f"@{question[9]}" if question[9] else "دبیر دیگر"
        await query.answer(
            QUESTION_TAKEN_BY_OTHER.format(teacher_name=teacher_name),
            show_alert=True
        )
        return

    await query.answer("✅ سؤال به شما تخصیص داده شد.")

    now = get_shamsi_now()
    timeout = (jdatetime.datetime.now() + jdatetime.timedelta(minutes=TEACHER_TIMEOUT_MINUTES)).strftime("%Y/%m/%d %H:%M:%S")

    update_question(
        question_id,
        status='taken',
        teacher_id=user_id,
        teacher_username=username,
        teacher_name=full_name or username,
        taken_time=now,
        timeout_time=timeout
    )

    context.user_data['active_question_id'] = question_id

    try:
        await query.edit_message_reply_markup(
            reply_markup=get_teacher_close_button(question_id)
        )
    except:
        pass

    await query.message.reply_text(
        TEACHER_ANSWER_REQUEST.format(
            code=question[3],
            username=username,
            timeout=TEACHER_TIMEOUT_MINUTES
        ),
        parse_mode="Markdown"
    )

    await query.message.reply_text(
        TEACHER_TAKEN_MSG.format(code=question[3]),
        parse_mode="Markdown"
    )


async def teacher_send_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    question_id = context.user_data.get('active_question_id')

    if not question_id:
        return
    if not is_teacher(user_id):
        return

    question = get_question(question_id)
    if not question:
        return
    if question[8] != user_id:
        return
    if question[7] == 'closed':
        context.user_data.pop('active_question_id', None)
        return

    student_id = question[1]
    try:
        await context.bot.copy_message(
            chat_id=student_id,
            from_chat_id=update.effective_chat.id,
            message_id=update.message.message_id
        )
    except Exception as e:
        print(f"Error sending answer to student: {e}")


async def teacher_close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    question_id = int(query.data.split("_")[2])

    if not is_teacher(user_id):
        await query.answer("⛔ شما دبیر نیستید.", show_alert=True)
        return

    question = get_question(question_id)
    if not question:
        await query.answer("⚠️ سؤال یافت نشد.", show_alert=True)
        return

    if question[8] != user_id and question[7] not in ('waiting', 'taken'):
        await query.answer("⛔ شما دبیر این سؤال نیستید.", show_alert=True)
        return

    await query.answer("✅ سؤال بسته شد.")

    now = get_shamsi_now()
    update_question(question_id, status='answered', answered_time=now, closed_time=now)

    if context.user_data.get('active_question_id') == question_id:
        context.user_data.pop('active_question_id', None)

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except:
        pass

    await query.message.reply_text(
        f"✅ سؤال `{question[3]}` بسته شد.",
        parse_mode="Markdown"
    )

    student_id = question[1]
    student = get_user(student_id)
    questions_left = student[8] if student else 0

    try:
        await context.bot.send_message(
            chat_id=student_id,
            text=(
                f"✅ *پاسخ سؤال شما ارسال شد.*\n\n"
                f"📚 درس: {question[2]}\n"
                f"🆔 کد سؤال: `{question[3]}`\n\n"
                f"📚 سوالات باقی‌مانده شما: {questions_left}\n\n"
                f"آیا متوجه شدید؟"
            ),
            reply_markup=get_student_answer_buttons(question_id),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Error sending to student: {e}")


async def student_understood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("✅ خوشحالیم که متوجه شدید!")
    question_id = int(query.data.split("_")[3])
    now = get_shamsi_now()
    update_question(question_id, status='closed', closed_time=now)
    try:
        await query.edit_message_text(
            "✅ *از اینکه از ویولکس استفاده کردید سپاسگزاریم.*\n\n"
            "موفق باشید! 🌟",
            parse_mode="Markdown"
        )
    except:
        pass


async def student_followup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    question_id = int(query.data.split("_")[3])
    context.user_data['followup_question_id'] = question_id
    context.user_data['awaiting_followup'] = True
    await query.message.reply_text(
        "🔁 *لطفاً سؤال تکمیلی خود را ارسال کنید.*\n\n"
        "⚠️ سؤال تکمیلی فقط درباره همان سؤال قبلی است.",
        parse_mode="Markdown"
    )


async def handle_followup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('awaiting_followup'):
        return False

    user = update.effective_user
    question_id = context.user_data.get('followup_question_id')
    text = update.message.text

    context.user_data['awaiting_followup'] = False

    question = get_question(question_id)
    if not question:
        await update.message.reply_text("⚠️ سؤال یافت نشد.")
        return True

    subject = question[2]
    subject_info = SUBJECTS.get(subject)

    if subject_info:
        try:
            await context.bot.send_message(
                chat_id=subject_info['group'],
                text=(
                    f"🔁 *سؤال تکمیلی برای کد:* `{question[3]}`\n\n"
                    f"👤 دانش‌آموز: @{user.username or 'ندارد'}\n"
                    f"📌 این سؤال باید توسط دبیر پاسخ داده شود.\n\n"
                    f"📝 *متن سؤال تکمیلی:*\n{text}"
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ پاسخ دادن", callback_data=f"t_answer_{question_id}", style="success")]
                ]),
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Error sending followup: {e}")

    await update.message.reply_text(
        "✅ *سؤال تکمیلی شما ارسال شد.*\n"
        "پاسخ از طریق همین ربات به شما اطلاع داده خواهد شد.",
        parse_mode="Markdown"
    )
    return True


# ============================================
# درباره ما - نمایش اطلاعات دبیران (فقط ویرایش)
# ============================================

async def show_teacher_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش اطلاعات اولین دبیر یک درس با ویرایش پیام"""
    query = update.callback_query
    await query.answer()

    data = query.data
    subject_map = {
        "about_biology": "زیست",
        "about_chemistry": "شیمی",
        "about_physics": "فیزیک",
        "about_math": "ریاضی",
    }

    subject = subject_map.get(data)
    if not subject:
        return

    teachers = TEACHERS_INFO.get(subject, [])
    if not teachers:
        await query.answer("⚠️ اطلاعاتی موجود نیست.", show_alert=True)
        return

    teacher = teachers[0]
    text = teacher['text']
    image_url = teacher.get('image')
    keyboard = get_teacher_navigation_buttons(subject, 0, len(teachers))

    try:
        # ویرایش پیام فعلی
        if image_url:
            await query.edit_message_media(
                media=InputMediaPhoto(
                    media=image_url,
                    caption=text,
                    parse_mode="Markdown"
                ),
                reply_markup=keyboard
            )
        else:
            await query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
    except Exception as e:
        print(f"Error show_teacher_bio: {e}")
        try:
            if image_url:
                await query.message.reply_photo(
                    photo=image_url,
                    caption=text,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            else:
                await query.message.reply_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
        except Exception as e2:
            print(f"Error show_teacher_bio (fallback): {e2}")


async def navigate_teacher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ناوبری بین دبیران (ویرایش، پاک نمی‌شود)"""
    query = update.callback_query
    await query.answer()

    data = query.data
    parts = data.split("_")
    subject = parts[2]
    index = int(parts[3])

    teachers = TEACHERS_INFO.get(subject, [])
    if not teachers or index < 0 or index >= len(teachers):
        await query.answer("⚠️ خطا در ناوبری.", show_alert=True)
        return

    teacher = teachers[index]
    text = teacher['text']
    image_url = teacher.get('image')
    keyboard = get_teacher_navigation_buttons(subject, index, len(teachers))

    try:
        if image_url:
            await query.edit_message_media(
                media=InputMediaPhoto(
                    media=image_url,
                    caption=text,
                    parse_mode="Markdown"
                ),
                reply_markup=keyboard
            )
        else:
            await query.edit_message_text(
                text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
    except Exception as e:
        print(f"Error navigate_teacher: {e}")
        try:
            if image_url:
                await query.message.reply_photo(
                    photo=image_url,
                    caption=text,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            else:
                await query.message.reply_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
        except Exception as e2:
            print(f"Error navigate_teacher (fallback): {e2}")


async def back_to_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بازگشت به لیست دبیران با عکس درباره ما"""
    query = update.callback_query
    await query.answer()

    try:
        # اگر عکس درباره ما وجود دارد، عکس رو با متن نمایش بده
        if ABOUT_IMAGE_URL:
            await query.edit_message_media(
                media=InputMediaPhoto(
                    media=ABOUT_IMAGE_URL,
                    caption=ABOUT_US_TEXT,
                    parse_mode="Markdown"
                ),
                reply_markup=get_about_buttons()
            )
        else:
            # اگر عکس نبود، فقط متن
            try:
                await query.edit_message_caption(
                    caption=ABOUT_US_TEXT,
                    reply_markup=get_about_buttons(),
                    parse_mode="Markdown"
                )
            except:
                await query.edit_message_text(
                    ABOUT_US_TEXT,
                    reply_markup=get_about_buttons(),
                    parse_mode="Markdown"
                )
    except Exception as e:
        print(f"Error back_to_about (edit): {e}")
        # اگر ویرایش نشد، پیام جدید بفرست (پیام قبلی رو پاک نکن)
        try:
            if ABOUT_IMAGE_URL:
                await query.message.reply_photo(
                    photo=ABOUT_IMAGE_URL,
                    caption=ABOUT_US_TEXT,
                    reply_markup=get_about_buttons(),
                    parse_mode="Markdown"
                )
            else:
                await query.message.reply_text(
                    ABOUT_US_TEXT,
                    reply_markup=get_about_buttons(),
                    parse_mode="Markdown"
                )
        except Exception as e2:
            print(f"Error back_to_about (fallback): {e2}")


# ============================================
# تایم اوت دبیران
# ============================================

async def check_teacher_timeouts(context: ContextTypes.DEFAULT_TYPE):
    expired = get_expired_questions()

    for question_id, code, teacher_id in expired:
        update_question(
            question_id,
            status='waiting',
            teacher_id=None,
            teacher_username=None,
            teacher_name=None,
            taken_time=None,
            timeout_time=None
        )

        question = get_question(question_id)
        if not question:
            continue

        subject = question[2]
        subject_info = SUBJECTS.get(subject)
        if not subject_info:
            continue

        try:
            student = get_user(question[1])
            username = student[1] if student else None

            await context.bot.send_message(
                chat_id=subject_info['group'],
                text=(
                    f"⏰ *سؤال بازگشت به صف*\n\n"
                    f"📚 درس: {subject}\n"
                    f"👤 دانش‌آموز: @{username or 'ندارد'}\n"
                    f"🆔 کد سؤال: `{code}`\n"
                    f"⚠️ دبیر قبلی در زمان مقرر پاسخ نداد.\n\n"
                    f"📝 لطفاً یکی از دبیران پاسخ دهد."
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ پاسخ دادن", callback_data=f"t_answer_{question_id}", style="success")]
                ]),
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Error sending timeout: {e}")

        if teacher_id:
            try:
                await context.bot.send_message(
                    chat_id=teacher_id,
                    text=TEACHER_TIMEOUT_MSG.format(code=code),
                    parse_mode="Markdown"
                )
            except:
                pass