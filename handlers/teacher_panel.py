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
from texts import TEACHER_ANSWER_REQUEST, TEACHER_BUSY, ABOUT_US_TEXT


# ============================================
# بررسی دبیر بودن کاربر
# ============================================

def is_teacher(user_id):
    return is_staff(user_id, role="teacher") or is_staff(user_id, role="owner") or is_staff(user_id, role="admin")


# ============================================
# اطلاعات دبیران (بیوگرافی)
# ============================================

TEACHER_BIOS = {
    "زیست": (
        "👤 *نام دبیر:* امیرپارسا زارعی\n"
        "🎓 *رشته تحصیلی:* پزشکی\n"
        "🏛️ *دانشگاه محل تحصیل:* دانشگاه علوم پزشکی شهید بهشتی\n"
        "📣 *فعالیت تخصصی دبیر:*\n"
        "🧬 *دبیر زیست* | 📌 *طراحی و ویراستاری آزمون*\n\n"
        "📌 *رزومه فردی:*\n"
        "✅ رتبه ۱۹۱ منطقه ۲ و ۴۰۰ کشور\n"
        "✅ بالاترین درصد زیست کنکور ۱۴۰۴\n"
        "✅ کسب درصد *۹۴٪* در کنکور اردیبهشت و *۹۷٪* در کنکور تیرماه\n\n"
        "💼 *رزومه شغلی و اجرایی:*\n"
        "🔸 ویراستار آزمون «زیستاز»\n"
        "🔸 طراح آزمون «آرمان»"
    ),
    "شیمی": (
        "👤 *نام دبیر:* امیررضا کیانی آسیابری\n"
        "🎓 *رشته تحصیلی:* پزشکی\n"
        "🏛️ *دانشگاه محل تحصیل:* دانشگاه علوم پزشکی گیلان\n"
        "📣 *فعالیت تخصصی دبیر:*\n"
        "🧪 *دبیر شیمی* | 📌 *مشاوره و برنامه‌ریزی تحصیلی*\n\n"
        "📌 *رزومه فردی:*\n"
        "✅ تنها معدل ۲۰ کل کشور\n"
        "✅ مدال مسابقات *IMC* (مسابقات جهانی ریاضی)\n"
        "✅ قبولی المپیادهای *شیمی، کامپیوتر و نجوم*\n\n"
        "💼 *رزومه شغلی و اجرایی:*\n"
        "🔸 عضو دپارتمان شیمی «سیب ترش»\n"
        "🔸 طراح سوالات آزمون‌های آزمایشی\n"
        "🔸 برگزارکننده همایش‌های مشاوره‌ای"
    ),
    "فیزیک": (
        "👤 *نام دبیر:* احمدرضا اسکندری\n"
        "🎓 *رشته تحصیلی:* پزشکی\n"
        "🏛️ *دانشگاه محل تحصیل:* دانشگاه علوم پزشکی گیلان\n"
        "📣 *فعالیت تخصصی دبیر:*\n"
        "⚡️ *دبیر فیزیک* | 👨‍🏫 *تدریس خصوصی* | 📌 *ویراستاری آزمون*\n\n"
        "💼 *رزومه شغلی و اجرایی:*\n"
        "🔸 برگزاری کلاس تدریس خصوصی\n"
        "🔸 سابقه همکاری با مدارس برتر رشت\n"
        "🔸 ویراستار آزمون‌های آزمایشی"
    ),
    "ریاضی": (
        "👤 *نام دبیر:* محمدرضا سروری\n"
        "🎓 *رشته تحصیلی:* مهندسی شیمی\n"
        "🏛️ *دانشگاه محل تحصیل:* دانشگاه صنعتی امیرکبیر\n"
        "📣 *فعالیت تخصصی دبیر:*\n"
        "⚡️ *دبیر فیزیک* | 📐 *دبیر ریاضی* | ✍️ *طراحی سوال* | 🎯 *جمع‌بندی و آمادگی آزمون*\n\n"
        "📌 *رزومه فردی:*\n"
        "✅ رتبه ۱۲۴۶\n"
        "✅ ریاضیات *۵۴٪* و فیزیک *۹۲٪*\n"
        "✅ مدال طلای المپیاد جهانی ریاضیات و علوم *ISMI*\n"
        "✅ رتبه ممتاز ورودی مهندسی شیمی دانشگاه صنعتی امیرکبیر\n"
        "✅ *رتبه ۵* آموزش ریاضی کنکور فرهنگیان\n\n"
        "💼 *رزومه شغلی و اجرایی:*\n"
        "🔸 طراح سوال\n"
        "🔸 برگزارکننده کلاس‌های جمع‌بندی برای مدارس برتر تهران\n"
        "🔸 برگزاری کلاس خصوصی"
    ),
}


# ============================================
# دکمه "پاسخ دادن" توسط دبیر
# ============================================

async def teacher_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    user_id = query.from_user.id
    data = query.data
    question_id = int(data.split("_")[2])

    if not is_teacher(user_id):
        await query.answer("⛔ شما دبیر نیستید.", show_alert=True)
        return

    active_id = context.user_data.get('active_question_id')
    if active_id and active_id != question_id:
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
        await query.answer("⚠️ این سؤال قبلاً توسط دبیر دیگری برداشته شده است.", show_alert=True)
        return

    await query.answer("✅ سؤال به شما تخصیص داده شد.")

    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    update_question(
        question_id,
        status='taken',
        teacher_id=user_id,
        taken_time=now
    )

    context.user_data['active_question_id'] = question_id

    try:
        await query.edit_message_reply_markup(
            reply_markup=get_teacher_close_button(question_id)
        )
    except:
        pass

    await query.message.reply_text(
        TEACHER_ANSWER_REQUEST.format(code=question[3])
    )


# ============================================
# دریافت پاسخ دبیر
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

    if question[8] != user_id and question[7] != 'waiting':
        await query.answer("⛔ شما دبیر این سؤال نیستید.", show_alert=True)
        return

    await query.answer("✅ سؤال بسته شد.")

    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    update_question(question_id, status='answered', closed_time=now)

    if context.user_data.get('active_question_id') == question_id:
        context.user_data.pop('active_question_id', None)

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except:
        pass

    await query.message.reply_text(
        f"✅ سؤال {question[3]} توسط دبیر بسته شد."
    )

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
# دکمه "متوجه شدم"
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
# دکمه "سوال تکمیلی"
# ============================================

async def student_followup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

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


# ============================================
# نمایش اطلاعات دبیر (درباره ما - با ویرایش پیام)
# ============================================

async def show_teacher_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش اطلاعات دبیر با ویرایش پیام"""
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

    bio_text = TEACHER_BIOS.get(subject, "اطلاعات موجود نیست.")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 بازگشت", callback_data="about_back")]
    ])

    try:
        await query.edit_message_text(
            bio_text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Error editing message: {e}")


async def back_to_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بازگشت به منوی درباره ما"""
    query = update.callback_query
    await query.answer()

    from keyboards import get_about_buttons

    try:
        await query.edit_message_text(
            ABOUT_US_TEXT,
            reply_markup=get_about_buttons(),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Error: {e}")