import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# توکن ربات
TOKEN = "8762301184:AAGbn9CZirNf7Yc9nRdnBpQMfFGEnu8r9wA"
# آیدی عددی کانال (با علامت منفی)
CHANNEL_ID = -1003858232624
# لینک کانال (برای دکمه)
CHANNEL_LINK = "https://t.me/violex_official"

# متن پیام اولیه (عضویت اجباری)
FORCE_MSG = (
    "سلام 👋\n"
    "به ربات آموزشی VIOLEX خوش آمدید ✨\n"
    "\n"
    "📚 برای استفاده از خدمات ربات لازم است ابتدا در کانال ما عضو شوید.\n"
    "\n"
    "پس از عضویت، روی دکمه بررسی عضویت بزنید تا دسترسی شما فعال شود.\n"
)

# متن پیام برای کاربرانی که عضو نشده‌اند
NOT_MEMBER_MSG = (
    "⛔ برای استفاده از ربات ابتدا عضو کانال شوید\n"
    "\n"
    "👇 سپس دوباره /start را بزنید"
)

# متن پیام برای کاربرانی که عضو شده‌اند
WELCOME_MSG = "✅ خوش آمدید! ربات فعال شد 🎉"

# منوی اصلی
MAIN_MENU_TEXT = (
    "*🏠 منوی اصلی ویولکس*\n"
    "از گزینه‌های زیر، بخش مورد نظر خود را انتخاب کنید 👇\n"
    "برای بازگشت همیشه می‌توانید دوباره به این منو بیایید 🌟"
)

# دکمه‌های اینلاین (فقط برای عضویت اجباری)
def get_force_buttons():
    keyboard = [
        [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_sub")],
    ]
    return InlineKeyboardMarkup(keyboard)

# دکمه‌های ریپلی کیبورد (منوی اصلی)
def get_main_menu_keyboard():
    keyboard = [
        [KeyboardButton("📚 ارسال سوال")],
        [KeyboardButton("🔙 برگشت")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# دکمه‌های ریپلی کیبورد (انتخاب درس)
def get_lesson_keyboard():
    keyboard = [
        [KeyboardButton("🔙 برگشت")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# تابع بررسی عضویت کاربر در کانال
async def is_user_member(application: Application, user_id: int) -> bool:
    try:
        member = await application.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False

# هندلر دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    # بررسی عضویت کاربر
    if await is_user_member(context.application, user_id):
        # اگر عضو است، پیام خوش‌آمدگویی بفرست
        await update.message.reply_text(WELCOME_MSG)
        # منوی اصلی را نمایش بده
        await update.message.reply_text(
            MAIN_MENU_TEXT,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )
    else:
        # اگر عضو نیست، پیام عضویت اجباری را با دکمه‌ها بفرست
        await update.message.reply_text(
            FORCE_MSG,
            reply_markup=get_force_buttons(),
            disable_web_page_preview=True,
        )

# هندلر دکمه‌ی بررسی عضویت
async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    message = query.message

    # بررسی مجدد عضویت
    if await is_user_member(context.application, user_id):
        # اگر عضو شده، پیام قبلی را حذف کن
        await message.delete()
        # پیام خوش‌آمدگویی جدید بفرست
        await query.message.reply_text(WELCOME_MSG)
        # منوی اصلی را نمایش بده
        await query.message.reply_text(
            MAIN_MENU_TEXT,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )
    else:
        # اگر عضو نشده، پیام فعلی را با پیام جدید جایگزین کن
        await query.edit_message_text(
            NOT_MEMBER_MSG,
            reply_markup=get_force_buttons(),
            disable_web_page_preview=True,
        )

# هندلر پیام‌های متنی
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    
    # بررسی عضویت برای همه‌ی پیام‌ها
    if not await is_user_member(context.application, user.id):
        await update.message.reply_text(
            "⛔ لطفاً ابتدا در کانال عضو شوید و سپس /start را بزنید.",
            reply_markup=get_force_buttons()
        )
        return
    
    if text == "📚 ارسال سوال":
        await update.message.reply_text(
            "📚 لطفاً درس مورد نظر خود را انتخاب کنید.",
            reply_markup=get_lesson_keyboard()
        )
    
    elif text == "🔙 برگشت":
        await update.message.reply_text(
            MAIN_MENU_TEXT,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )
    
    else:
        # پیام‌های دیگر
        await update.message.reply_text(
            "⚠️ لطفاً از گزینه‌های منو استفاده کنید.",
            reply_markup=get_main_menu_keyboard()
        )

# تابع اصلی برای اجرای ربات
def main():
    # اپلیکیشن را بساز
    app = Application.builder().token(TOKEN).build()

    # ثبت هندلرها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_subscription, pattern="check_sub"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # شروع ربات
    print("ربات در حال اجراست...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
