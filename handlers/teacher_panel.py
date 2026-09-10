from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import SUBJECTS
from database import (
    get_question, update_question, is_staff
)
from keyboards import (
    get_teacher_close_button, get_student_answer_buttons
)
from texts import TEACHER_ANSWER_REQUEST, TEACHER_BUSY


# ============================================
# بررسی دبیر بودن کاربر
# ============================================

def is_teacher(user_id):
    return is_staff(user_id, role="teacher") or is_staff(user_id, role="owner") or is_staff(user_id, role="admin")


# ============================================
# دکمه "پاسخ دادن" توسط دبیر
# ============================================

async def teacher_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    user_id = query.from_user.id
    data = query.data
    question_id = int(data.split("_")[2])

    # بررسی دبیر بودن
    if not is_teacher(user_id):
        await query.answer("⛔ شما دبیر نیستید.", show_alert=True)
        return

    # بررسی اینکه دبیر سوال دیگری در دست ندارد
    active_id = context.user_data.get('active_question_id')
    if active_id and active_id != question_id:
        await query.answer(TEACHER_BUSY, show_alert=True)
        return

    question = get_question(question_id)
    if not question:
        await query.answer("⚠️ سؤال یافت نشد.", show_alert=True)
        return

    # بررسی وضعیت سؤال
    if question[7] not in ('waiting', 'taken'):
        await query.answer("⚠️ این سؤال قبلاً بسته شده است.", show_alert=True)
        return

    # اگر قبلاً توسط دبیر دیگری برداشته شده
    if question[7] == 'taken' and question[8] != user_id:
        await query.answer("⚠️ این سؤال قبلاً توسط دبیر دیگری برداشته شده است.", show_alert=True)
        return

    await query.answer("✅ سؤال به شما تخصیص داده شد.")

    # تخصیص سؤال به دبیر
    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    update_question(
        question_id,
        status='taken',
        teacher_id=user_id,
        taken_time=now
    )

    context.user_data['active_question_id'] = question_id

    # ویرایش پیام اصلی (حذف دکمه پاسخ و گذاشتن فقط بستن)
    try:
        await query.edit_message_reply_markup(
            reply_markup=get_teacher_close_button(question_id)
        )
    except:
        pass

    # پیام به دبیر
    await query.message.reply_text(
        TEACHER_ANSWER_REQUEST.format(code=question[3])
    )


# ============================================
# دریافت پاسخ دبیر و ارسال به دانش‌آموز
# ============================================

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

    # اگر سؤال بسته شده
    if question[7] == 'closed':
        context.user_data.pop('active_question_id', None)
        return

    student_id = question[1]

    # فوروارد پیام به دانش‌آموز
    try:
        await context.bot.copy_message(
            chat_id=student_id,
            from_chat_id=update.effective_chat.id,
            message_id=update.message.message_id
        )
    except Exception as e:
        print(f"Error sending answer to student: {e}")
        try:
            await update.message.reply_text(
                f"⚠️ خطا در ارسال به دانش‌آموز: {e}"
            )
        except:
            pass


# ============================================
# بستن سؤال توسط دبیر
# ============================================

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

    # بررسی اینکه دبیر همین سؤال را داشته
    if question[8] != user_id and question[7] != 'waiting':
        await query.answer("⛔ شما دبیر این سؤال نیستید.", show_alert=True)
        return

    await query.answer("✅ سؤال بسته شد.")

    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    update_question(question_id, status='answered', closed_time=now)

    # پاک کردن active_question_id
    if context.user_data.get('active_question_id') == question_id:
        context.user_data.pop('active_question_id', None)

    # ویرایش پیام
    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except:
        pass

    # پیام به گروه
    await query.message.reply_text(
        f"✅ سؤال {question[3]} توسط دبیر بسته شد."
    )

    # پیام به دانش‌آموز
    student_id = question[1]
    try:
        await context.bot.send_message(
            chat_id=student_id,
            text=(
                f"✅ پاسخ سؤال شما ارسال شد.\n\n"
                f"🆔 کد سؤال: {question[3]}\n\n"
                f"آیا متوجه شدید؟"
            ),
            reply_markup=get_student_answer_buttons(question_id)
        )
    except Exception as e:
        print(f"Error sending to student: {e}")


# ============================================
# دکمه "متوجه شدم" توسط دانش‌آموز
# ============================================

async def student_understood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("✅ خوشحالیم که متوجه شدید!")

    question_id = int(query.data.split("_")[3])
    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    update_question(question_id, status='closed', closed_time=now)

    try:
        await query.edit_message_text(
            "✅ از اینکه از ویولکس استفاده کردید سپاسگزاریم.\n\n"
            "موفق باشید! 🌟"
        )
    except:
        pass


# ============================================
# دکمه "سوال تکمیلی" توسط دانش‌آموز
# ============================================

async def student_followup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    question_id = int(query.data.split("_")[3])

    context.user_data['followup_question_id'] = question_id
    context.user_data['awaiting_followup'] = True

    await query.message.reply_text(
        "🔁 لطفاً سؤال تکمیلی خود را ارسال کنید.\n\n"
        "⚠️ سؤال تکمیلی فقط درباره همان سؤال قبلی است."
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
                    f"🔁 سؤال تکمیلی برای کد: {question[3]}\n\n"
                    f"👤 دانش‌آموز: @{user.username or 'ندارد'}\n"
                    f"📌 این سؤال باید توسط دبیر پاسخ داده شود.\n\n"
                    f"📝 متن سؤال تکمیلی:\n{text}"
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("پاسخ دادن ✅", callback_data=f"t_answer_{question_id}")]
                ])
            )
        except Exception as e:
            print(f"Error sending followup: {e}")

    await update.message.reply_text(
        "✅ سؤال تکمیلی شما ارسال شد.\n"
        "پاسخ از طریق همین ربات به شما اطلاع داده خواهد شد."
    )
    return True