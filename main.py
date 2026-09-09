import asyncio
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# توکن ربات
TOKEN = "8762301184:AAGbn9CZirNf7Yc9nRdnBpQMfFGEnu8r9wA"
# آیدی عددی کانال (با علامت منفی)
CHANNEL_ID = -1003858232624
# لینک کانال (برای دکمه)
CHANNEL_LINK = "https://t.me/violex_official"
# لینک ربات برای دعوت
BOT_LINK = "https://ble.ir/VIOLEXQ_BOT?start="

# 🔴 لینک عکس درباره ما را اینجا قرار دهید 🔴
ABOUT_IMAGE_URL = "https://your-image-link.com/violex-about.jpg"  # <-- لینک عکس خود را جایگزین کنید

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

# متن پیام خوش‌آمدگویی جدید
WELCOME_MSG = (
    "سلام 👋\n"
    "به ربات آموزشی VIOLEX خوش آمدید.\n"
    "\n"
    "📚 در این ربات می‌توانید سوالات درسی خود را برای دبیران متخصص ارسال کنید و پاسخ کامل دریافت کنید.\n"
    "✅ پاسخ‌ها توسط دبیران بررسی می‌شود\n"
    "✅ پرداخت‌ها از طریق درگاه امن انجام می‌شود\n"
    "✅ تمام سفارش‌ها دارای کد پیگیری هستند\n"
    "\n"
    "یکی از گزینه‌های زیر را انتخاب کنید 👇"
)

# منوی اصلی
MAIN_MENU_TEXT = (
    "*🏠 منوی اصلی ویولکس*\n"
    "از گزینه‌های زیر، بخش مورد نظر خود را انتخاب کنید 👇\n"
    "برای بازگشت همیشه می‌توانید دوباره به این منو بیایید 🌟"
)

# متن منوی افزایش موجودی
INCREASE_BALANCE_TEXT = (
    "🔹 لطفاً یکی از گزینه‌های زیر را انتخاب کنید 👇"
)

# متن احراز هویت
AUTH_TEXT = (
    "🪪 *برای استفاده از خدمات ربات، ابتدا احراز هویت خود را تکمیل کنید.*  \n"
    "این مرحله برای امنیت پرداخت‌ها و اطمینان از استفاده از *کارت بانکی به نام صاحب حساب کاربری* الزامی است 💳✅\n"
    "\n"
    "پس از تکمیل احراز هویت، امکان پرداخت و ثبت سؤال برای شما فعال خواهد شد."
)

# متن قوانین ربات
RULES_TEXT = (
    "*📚🤖 قوانین استفاده از ربات «📚 ویولکس | کلینیک رفع اشکال کنکور»*\n"
    "سلام دوست کنکوری من 👋📖  \n"
    "ویولکس برای این ساخته شده که *در سریع‌ترین زمان ممکن، پاسخ دقیق سؤالات درسی شما را ارائه دهد.* \n"
    "برای اینکه این سیستم برای همه کاربران *سریع، منصفانه و باکیفیت* باقی بماند، رعایت قوانین زیر ضروری است.\n"
    "📱 برای شروع، لطفاً روی دکمه *«ارسال شماره»* بزنید و *شماره تلفن خودتان* را ارسال کنید.\n"
    "✅ با وارد کردن *کد تأیید پیامکی* و ادامه استفاده از ربات، شما تأیید می‌کنید که این قوانین را مطالعه کرده و می‌پذیرید.\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "*👤 1. حساب کاربری و مسئولیت استفاده  \n"
    "حساب شما بر اساس *شماره تلفن همراه ثبت‌شده* ایجاد می‌شود.*\n"
    "به همین دلیل:  \n"
    "• تمام فعالیت‌های انجام‌شده از طریق حساب، مسئولیتش با صاحب همان شماره است.  \n"
    "• استفاده مشترک از حساب یا واگذاری آن به دیگران مجاز نیست.  \n"
    "• ساخت چند حساب برای یک نفر یا استفاده از حساب دیگران خلاف قوانین است.\n"
    "⚠️ در صورت مشاهده این موارد، حساب کاربر ممکن است محدود یا مسدود شود.\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "*❓ 2. قانون اصلی ربات (هر درخواست = یک سؤال)  *\n"
    "برای حفظ سرعت پاسخ‌دهی:\n"
    "✅ هر درخواست باید فقط شامل *یک سؤال* باشد.  \n"
    "نمونه‌های مجاز:  \n"
    "• یک تست  \n"
    "• یک مسئله  \n"
    "• یک تصویر از یک سؤال\n"
    "نمونه‌های غیرمجاز:  \n"
    "❌ چند تست در یک تصویر  \n"
    "❌ ارسال یک صفحه کامل از کتاب با چند سؤال  \n"
    "❌ چند سؤال در یک پیام  \n"
    "❌ سؤال چندبخشی برای گرفتن چند پاسخ\n"
    "⚠️ اگر چند سؤال در یک پیام یا تصویر ارسال شود:  \n"
    "درخواست *به عنوان یک ثبت سؤال محسوب شده و اعتبار آن کسر می‌شود* حتی اگر پاسخ کامل ارائه نشود.\n"
    "📌 این قانون برای جلوگیری از شلوغ شدن صف پاسخ و حفظ عدالت بین کاربران است.\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "*🧠 3. جلوگیری از دور زدن قوانین*  \n"
    "سیستم ویولکس الگوهای استفاده از ربات را بررسی می‌کند تا همه کاربران فرصت برابر داشته باشند.\n"
    "نمونه‌هایی از تلاش برای دور زدن قوانین:\n"
    "❌ قرار دادن چند سؤال در یک تصویر  \n"
    "❌ ارسال سؤال چندبخشی برای گرفتن چند پاسخ  \n"
    "❌ ارسال ادامه سؤال در پیام بعدی برای دور زدن محدودیت  \n"
    "❌ استفاده از چند حساب برای یک نفر  \n"
    "❌ ارسال سؤال جدید در قالب سؤال تکمیلی\n"
    "در صورت تشخیص این موارد ممکن است:\n"
    "⚠️ درخواست بدون پاسخ ثبت شود  \n"
    "⚠️ اعتبار کسر شود  \n"
    "⚠️ حساب کاربر به‌صورت موقت یا دائم محدود شود\n"
    "📌 رعایت قوانین باعث می‌شود پاسخ‌ها *سریع‌تر و دقیق‌تر* به دست همه کاربران برسد.\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "*💳 4. قوانین پرداخت و واریز*\n"
    "برای جلوگیری از سوءاستفاده مالی و حفظ امنیت کاربران:\n"
    "✅ پرداخت و واریز باید فقط با کارت بانکی ثبت‌شده به نام صاحب حساب کاربری انجام شود.\n"
    "موارد زیر مجاز نیست:\n"
    "❌ واریز با کارت بانکی افراد دیگر\n"
    "❌ استفاده از کارت دوستان یا آشنایان\n"
    "❌ استفاده از کارت اجاره‌ای\n"
    "❌ ثبت پرداخت از حسابی که متعلق به صاحب شماره تلفن نیست\n"
    "⚠️ در صورت مشاهده مغایرت بین صاحب حساب کاربری و کارت پرداختی ممکن است:\n"
    "• پرداخت تأیید نشود\n"
    "• اعتبار به حساب اضافه نشود\n"
    "• حساب کاربر برای بررسی بیشتر محدود شود\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "*🎯 5. کسر اعتبار برای هر سؤال*  \n"
    "با ثبت هر سؤال:\n"
    "➖ یک واحد اعتبار از حساب شما کسر می‌شود.\n"
    "ثبت سؤال به معنای *شروع فرآیند بررسی توسط تیم آموزشی* است، بنابراین پس از ثبت درخواست:\n"
    "❌ امکان لغو یا بازگشت اعتبار وجود ندارد  \n"
    "✅ مگر در صورت تشخیص خطای فنی توسط سامانه\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "*💬 6. سؤالات تکمیلی*  \n"
    "اگر بعد از دریافت پاسخ هنوز بخشی از توضیح را متوجه نشدید، می‌توانید از طریق *دکمه‌های زیر همان پاسخ* سؤال تکمیلی بپرسید.\n"
    "✅ سؤال تکمیلی فقط درباره همان سؤال قبلی است  \n"
    "❌ ارسال سؤال جدید در این بخش مجاز نیست\n"
    "📌 این بخش برای *درک بهتر پاسخ* طراحی شده است.\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "*📩 7. محتوای ارسالی*  \n"
    "برای حفظ فضای آموزشی سالم، ارسال موارد زیر مجاز نیست:\n"
    "❌ پیام‌های نامرتبط با درس  \n"
    "❌ پیام‌های توهین‌آمیز  \n"
    "❌ تبلیغات یا اسپم\n"
    "در صورت تکرار، دسترسی کاربر ممکن است محدود شود.\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "*⏳ 8. زمان پاسخ‌دهی*  \n"
    "تیم آموزشی ویولکس تلاش می‌کند سؤالات را در *کوتاه‌ترین زمان ممکن* بررسی و پاسخ دهد.\n"
    "زمان پاسخ‌دهی ممکن است بسته به *تعداد سؤالات در صف* متفاوت باشد.\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "*🛠️ 9. اختلالات فنی*  \n"
    "در صورت بروز مشکل فنی در سامانه، تیم پشتیبانی آن را بررسی خواهد کرد.\n"
    "در صورت تأیید خطای فنی:  \n"
    "✅ اعتبار کسرشده قابل بازگشت خواهد بود.\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "*🔄 10. به‌روزرسانی قوانین*  \n"
    "برای بهبود کیفیت خدمات، ممکن است این قوانین در آینده به‌روزرسانی شوند.  \n"
    "ادامه استفاده از ربات به معنای *پذیرش نسخه جدید قوانین* خواهد بود."
)

# متن تأیید قوانین
CONFIRM_RULES_TEXT = (
    "✅ *تأیید قوانین*\n"
    "با وارد کردن *کد تأیید پیامکی* و ادامه استفاده از ربات ویولکس، شما اعلام می‌کنید که:\n"
    "✔️ قوانین را مطالعه کرده‌اید  \n"
    "✔️ مسئولیت استفاده از حساب خود را می‌پذیرید  \n"
    "✔️ متعهد به رعایت قوانین سامانه هستید\n"
    "🎯 هدف این قوانین یک چیز است:  \n"
    "ارائه *پاسخ سریع، دقیق و عادلانه* برای همه دانش‌آموزان.\n"
    "\n"
    "*📨 لطفاً کد تأیید ارسال‌شده را وارد کنید.*"
)

# متن درباره ما
ABOUT_US_TEXT = (
    "📚 *در مسیر آمادگی برای کنکور، تمرین و حل تست یکی از مهم‌ترین بخش‌های یادگیری است.*\n"
    "اما گاهی حتی با وجود پاسخنامه هم ممکن است روش حل سؤال را به‌ خوبی متوجه نشوید یا در بخشی از حل دچار ابهام شوید. 🤔\n"
    "💠 *ویولکس دقیقاً برای همین ساخته شده است.*\n"
    "فضایی برای *رفع اشکال دقیق و شخصی‌سازی‌شده* که در آن سؤالات شما توسط *دبیران متخصص هر درس* بررسی می‌شود و *پاسخ تشریحی و قابل فهم* دریافت می‌کنید. 👨‍🏫📖\n"
    "✅ کافی است سؤال خود را ارسال کنید تا پاسخ آن توسط دبیر مربوطه بررسی و توضیح داده شود.\n"
    "👨‍🏫 همچنین می‌توانید از طریق دکمه‌های *زیر این بخش*، با *دبیر هر درس و سوابق آموزشی آن‌ها* بیشتر آشنا شوید."
)

# دکمه‌های اینلاین (فقط برای عضویت اجباری)
def get_force_buttons():
    keyboard = [
        [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_sub")],
    ]
    return InlineKeyboardMarkup(keyboard)

# دکمه‌های اینلاین برای افزایش موجودی
def get_balance_buttons():
    keyboard = [
        [InlineKeyboardButton("احراز هویت 🪪", callback_data="auth")],
        [InlineKeyboardButton("خرید پکیج 📦", callback_data="buy_package")],
        [InlineKeyboardButton("خرید سوال ❓", callback_data="buy_question")],
        [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

# دکمه‌های اینلاین برای احراز هویت
def get_auth_buttons():
    keyboard = [
        [InlineKeyboardButton("لیست کارت‌ها 🧾", callback_data="card_list")],
        [InlineKeyboardButton("افزودن کارت ➕", callback_data="add_card")],
        [InlineKeyboardButton("حذف کارت ➖", callback_data="remove_card")],
        [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

# دکمه‌های اینلاین برای قوانین (فقط منوی اصلی)
def get_rules_buttons():
    keyboard = [
        [InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(keyboard)

# دکمه‌های اینلاین برای درباره ما (دکمه‌های درس - فقط نمایش)
def get_about_buttons():
    keyboard = [
        [InlineKeyboardButton("🧬 زیست", callback_data="about_biology")],
        [InlineKeyboardButton("🧪 شیمی", callback_data="about_chemistry")],
        [InlineKeyboardButton("⚡️ فیزیک", callback_data="about_physics")],
        [InlineKeyboardButton("📐 ریاضی", callback_data="about_math")],
    ]
    return InlineKeyboardMarkup(keyboard)

# دکمه‌های ریپلی کیبورد (منوی اصلی)
def get_main_menu_keyboard():
    keyboard = [
        [KeyboardButton("📚 ارسال سوال"), KeyboardButton("💸 افزایش موجودی")],
        [KeyboardButton("👤 حساب من"), KeyboardButton("🤝 دعوت دوستان")],
        [KeyboardButton("☎️ پشتیبانی"), KeyboardButton("📋 درباره ما")],
        [KeyboardButton("🆘 قوانین"), KeyboardButton("📖 راهنما")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# دکمه‌های ریپلی کیبورد (برای قوانین - ثبت شماره)
def get_rules_keyboard():
    keyboard = [
        [KeyboardButton("📱 ثبت شماره خود")],
        [KeyboardButton("🔙 برگشت")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# دکمه‌های ریپلی کیبورد (انتخاب درس) - چیدمان ۲×۲
def get_lesson_keyboard():
    keyboard = [
        [KeyboardButton("🧬 زیست"), KeyboardButton("🧪 شیمی")],
        [KeyboardButton("⚡️ فیزیک"), KeyboardButton("📐 ریاضی")],
        [KeyboardButton("🔙 برگشت")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# دکمه‌های اینلاین برای پیام "خرید پکیج" بعد از انتخاب درس
def get_buy_package_button():
    keyboard = [
        [InlineKeyboardButton("خرید پکیج 📦", callback_data="buy_package")],
    ]
    return InlineKeyboardMarkup(keyboard)

# دکمه‌های اینلاین برای پیام "احراز هویت" بعد از خرید پکیج
def get_auth_button():
    keyboard = [
        [InlineKeyboardButton("احراز هویت 🪪", callback_data="auth")],
    ]
    return InlineKeyboardMarkup(keyboard)

# تابع بررسی عضویت کاربر در کانال
async def is_user_member(application: Application, user_id: int) -> bool:
    try:
        member = await application.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False

# تابع تولید لینک دعوت
def get_referral_link(user_id: int) -> str:
    return f"{BOT_LINK}{user_id}"

# تابع تولید نام تصادفی
def generate_random_name() -> str:
    first_names = ["علی", "محمد", "حسین", "رضا", "مهدی", "سارا", "فاطمه", "زهرا", "نگین", "آرین"]
    last_names = ["احمدی", "محمدی", "کریمی", "رضایی", "حسینی", "یزدانی", "نوری", "موسوی", "صادقی", "مرادی"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

# دیتای کاربران (در حالت واقعی از دیتابیس استفاده می‌شود)
user_data = {}

def get_user_info(user_id: int) -> dict:
    if user_id not in user_data:
        user_data[user_id] = {
            'user_id': user_id,
            'name': generate_random_name(),
            'phone': '0912***7890',
            'questions_left': random.randint(0, 20),
            'questions_used': random.randint(0, 50),
            'balance': random.randint(1000000, 50000000),
            'active_package': random.choice(['0', 'پایه', 'استاندارد', 'حرفه‌ای']),
            'expiry_date': random.choice(['-', '1405/07/15', '1405/08/01', '1405/09/10']),
            'referrals': random.randint(0, 15),
            'has_card': random.choice([True, False]),
            'has_active_package': random.choice([True, False])
        }
    return user_data[user_id]

# هندلر دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # ذخیره اطلاعات کاربر
    get_user_info(user_id)

    # بررسی عضویت کاربر
    if await is_user_member(context.application, user_id):
        # اگر عضو است، پیام خوش‌آمدگویی جدید بفرست
        await update.message.reply_text(
            WELCOME_MSG,
            reply_markup=get_main_menu_keyboard()
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
        await query.message.reply_text(
            WELCOME_MSG,
            reply_markup=get_main_menu_keyboard()
        )
    else:
        # اگر عضو نشده، پیام فعلی را با پیام جدید جایگزین کن
        await query.edit_message_text(
            NOT_MEMBER_MSG,
            reply_markup=get_force_buttons(),
            disable_web_page_preview=True,
        )

# هندلر دکمه‌های اینلاین افزایش موجودی
async def handle_balance_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "auth":
        await query.edit_message_text(
            AUTH_TEXT,
            reply_markup=get_auth_buttons(),
            parse_mode="Markdown"
        )
    
    elif data == "buy_package":
        # بررسی اینکه کاربر کارت دارد یا نه
        user_info = get_user_info(query.from_user.id)
        if not user_info['has_card']:
            await query.edit_message_text(
                "*❗ شما هنوز کارت بانکی فعالی ثبت نکرده‌اید. لطفاً از بخش «احراز هویت» برای افزودن کارت اقدام کنید.*",
                reply_markup=get_auth_button(),
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                "📦 خرید پکیج\n\n"
                "پکیج‌های موجود:\n"
                "1️⃣ پکیج پایه - ۱۰۰,۰۰۰ تومان\n"
                "2️⃣ پکیج استاندارد - ۲۵۰,۰۰۰ تومان\n"
                "3️⃣ پکیج حرفه‌ای - ۵۰۰,۰۰۰ تومان\n\n"
                "لطفاً شماره پکیج مورد نظر را وارد کنید.",
                reply_markup=get_balance_buttons()
            )
    
    elif data == "buy_question":
        await query.edit_message_text(
            "❓ خرید سوال\n\n"
            "قیمت هر سوال: ۱۰,۰۰۰ تومان\n"
            "لطفاً تعداد سوالات مورد نیاز خود را وارد کنید.",
            reply_markup=get_balance_buttons()
        )
    
    elif data == "back_to_main":
        # حذف پیام قبلی
        await query.message.delete()
        # نمایش منوی اصلی
        await query.message.reply_text(
            MAIN_MENU_TEXT,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )

# هندلر دکمه‌های احراز هویت
async def handle_auth_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    user_info = get_user_info(user_id)
    
    if data == "card_list":
        if user_info['has_card']:
            await query.edit_message_text(
                "🧾 لیست کارت‌ها\n\n"
                "✅ شما یک کارت فعال دارید.\n"
                f"شماره کارت: ۶۰۳۷****{random.randint(1000, 9999)}",
                reply_markup=get_auth_buttons()
            )
        else:
            await query.edit_message_text(
                "🧾 لیست کارت‌ها\n\n"
                "شما هیچ کارتی ثبت نکرده‌اید.\n"
                "برای افزودن کارت جدید، روی دکمه 'افزودن کارت' کلیک کنید.",
                reply_markup=get_auth_buttons()
            )
    
    elif data == "add_card":
        # کاربر کارت اضافه می‌کند
        user_info['has_card'] = True
        await query.edit_message_text(
            "✅ کارت شما با موفقیت ثبت شد!\n\n"
            "شماره کارت: ۶۰۳۷****1234\n"
            "نام صاحب کارت: صاحب حساب",
            reply_markup=get_auth_buttons()
        )
    
    elif data == "remove_card":
        if user_info['has_card']:
            user_info['has_card'] = False
            await query.edit_message_text(
                "✅ کارت شما با موفقیت حذف شد.",
                reply_markup=get_auth_buttons()
            )
        else:
            await query.edit_message_text(
                "⚠️ شما هیچ کارتی برای حذف ندارید.",
                reply_markup=get_auth_buttons()
            )
    
    elif data == "back_to_main":
        # حذف پیام قبلی
        await query.message.delete()
        # نمایش منوی اصلی
        await query.message.reply_text(
            MAIN_MENU_TEXT,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )

# هندلر دکمه‌های درباره ما (فعلاً فقط نمایش)
async def handle_about_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # این دکمه‌ها فعلاً هیچ کاری نمی‌کنند
    pass

# هندلر دریافت شماره تلفن
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    contact = update.message.contact
    
    if contact:
        phone_number = contact.phone_number
        # ذخیره شماره در context برای استفاده بعدی
        context.user_data['phone_number'] = phone_number
        
        # ارسال پیام تأیید قوانین
        await update.message.reply_text(
            CONFIRM_RULES_TEXT,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "⚠️ لطفاً شماره خود را از طریق دکمه 'ثبت شماره خود' ارسال کنید.",
            reply_markup=get_rules_keyboard()
        )

# هندلر پیام‌های متنی
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    user_id = user.id
    user_info = get_user_info(user_id)
    
    # بررسی عضویت برای همه‌ی پیام‌ها
    if not await is_user_member(context.application, user.id):
        await update.message.reply_text(
            "⛔ لطفاً ابتدا در کانال عضو شوید و سپس /start را بزنید.",
            reply_markup=get_force_buttons()
        )
        return
    
    # دکمه "حساب من"
    if text == "👤 حساب من":
        now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        # اطلاعات واقعی از دیتای کاربر
        name_parts = user_info['name'].split()
        first_name = name_parts[0] if len(name_parts) > 0 else "کاربر"
        last_name = name_parts[1] if len(name_parts) > 1 else "عزیز"
        
        await update.message.reply_text(
            f"👤 حساب من\n"
            f"🆔 شناسه سیستمی شما: {user_id}\n"
            f"🆔 آی دی: @support_violex\n"
            f"👤 نام : {first_name} | {last_name}\n"
            f"📚 سوالات باقی مانده: {user_info['questions_left']}\n"
            f"📅 سوالات استفاده شده: {user_info['questions_used']}\n"
            f"💰 موجودی کیف پول: {user_info['balance']:,} ريال\n"
            f"🎁 پکیج فعال: {user_info['active_package']}\n"
            f"⏳ اعتبار تا: {user_info['expiry_date']}\n"
            f"👤 تعداد زیرمجموعه: {user_info['referrals']}\n"
            f"⏳ زمان استعلام: {now}",
            reply_markup=get_main_menu_keyboard()
        )
    
    # دکمه "دعوت دوستان"
    elif text == "🤝 دعوت دوستان":
        referral_link = get_referral_link(user_id)
        await update.message.reply_text(
            f"🚀 VIOLEX | کلینیک VIP رفع اشکال\n"
            f"✨ یادگیری با لذت، موفقیت با اطمینان\n\n"
            f"اگه توی حل تست‌ها هنوز بعضی نکات رو کامل متوجه نشدی یا موقع تست‌زنی یه جاهایی گیر می‌کنی،\n"
            f"وقتشه وارد جمع حرفه‌ای‌ها بشی!\n\n"
            f"💎 ویولِکس دقیقا برای همین ساخته شده:\n"
            f"فقط سؤال رو بفرست،\n"
            f"و در کوتاه‌ترین زمان، دبیر تخصصیِ همون درس، برات شخصی‌سازی‌شده،سوال را رفع اشکال می‌کنه.\n\n"
            f"🔥 اگه می‌خوای تو هم از این تجربه خاص استفاده کنی، از همین لینک شروع کن:\n"
            f"{referral_link}\n"
            f"ویولکس مسیر یادگیری رو برات هموار می‌کنه."
        )
        await update.message.reply_text(
            f"👥لینک دعوتتو برای دوستات بفرست تا اونا هم استفاده کنن؛ هرکی با لینک تو وارد بشه، یه هدیه برات ثبت میشه.\n\n"
            f"🎁 هدیه ما به شما برای هر دعوت موفق:  \n"
            f"۴٬۰۰۰ تومان\n\n"
            f"📢 هر کاربری که:\n"
            f"1️⃣ از طریق لینک شما وارد ربات شود  \n"
            f"2️⃣ ربات را استارت کند \n"
            f"3️⃣ در کانال عضو شود\n"
            f"✅ به عنوان زیرمجموعه شما ثبت می‌شود.\n"
            f"💰 بابت هر زیرمجموعه:  4,000 تومان به کیف پول شما اضافه خواهد شد.",
            reply_markup=get_main_menu_keyboard()
        )
    
    # دکمه "درباره ما" - با ارسال عکس
    elif text == "📋 درباره ما":
        await update.message.reply_photo(
            photo=ABOUT_IMAGE_URL,
            caption=ABOUT_US_TEXT,
            reply_markup=get_about_buttons(),
            parse_mode="Markdown"
        )
    
    # دکمه‌های منوی اصلی که فعلاً کاری نمی‌کنند
    elif text in ["☎️ پشتیبانی", "🆘 قوانین", "📖 راهنما"]:
        # این دکمه‌ها فعلاً هیچ کاری نمی‌کنند
        pass
    
    # دکمه "ارسال سوال"
    elif text == "📚 ارسال سوال":
        # بررسی اینکه کاربر پکیج فعال دارد یا نه
        if not user_info['has_active_package']:
            await update.message.reply_text(
                "❌ شما هیچ پکیج فعالی ندارید؛ برای ثبت سؤال ابتدا از بخش *«خرید پکیج»* اشتراک موردنظر خود را تهیه کنید.",
                reply_markup=get_buy_package_button(),
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "📚 لطفاً درس مورد نظر خود را انتخاب کنید.",
                reply_markup=get_lesson_keyboard()
            )
    
    elif text == "💸 افزایش موجودی":
        await update.message.reply_text(
            INCREASE_BALANCE_TEXT,
            reply_markup=get_balance_buttons()
        )
    
    elif text == "📱 ثبت شماره خود":
        # درخواست شماره تلفن با استفاده از دکمه درخواست شماره
        keyboard = [[KeyboardButton("📱 ارسال شماره", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            "📱 لطفاً برای ادامه، شماره تلفن خود را ارسال کنید:",
            reply_markup=reply_markup
        )
    
    # انتخاب درس
    elif text in ["🧬 زیست", "🧪 شیمی", "⚡️ فیزیک", "📐 ریاضی"]:
        # بررسی اینکه کاربر پکیج فعال دارد یا نه
        if not user_info['has_active_package']:
            await update.message.reply_text(
                "❌ شما هیچ پکیج فعالی ندارید؛ برای ثبت سؤال ابتدا از بخش *«خرید پکیج»* اشتراک موردنظر خود را تهیه کنید.",
                reply_markup=get_buy_package_button(),
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                f"✅ درس {text} انتخاب شد!\n\n"
                "📝 لطفاً سوال خود را به همراه فایل (در صورت وجود) ارسال کنید.\n"
                "پشتیبانان ما در اسرع وقت پاسخ خواهند داد.",
                reply_markup=get_lesson_keyboard()
            )
    
    elif text == "🔙 برگشت":
        # برگشت به منوی اصلی
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
    app.add_handler(CallbackQueryHandler(handle_balance_buttons, pattern="^(auth|buy_package|buy_question|back_to_main)$"))
    app.add_handler(CallbackQueryHandler(handle_auth_buttons, pattern="^(card_list|add_card|remove_card|back_to_main)$"))
    app.add_handler(CallbackQueryHandler(handle_about_buttons, pattern="^(about_biology|about_chemistry|about_physics|about_math)$"))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # شروع ربات
    print("ربات در حال اجراست...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
