import os

# ============================================
# تنظیمات ربات VIOLEX
# ============================================

# ---------- توکن ربات ----------
TOKEN = os.environ.get("BOT_TOKEN", "8849773001:AAFY4Uqiz16PCJNjZv7loZYPhIDKraBFpHc")

# ---------- کانال جوین اجباری ----------
CHANNEL_ID = -1003858232624
CHANNEL_LINK = "https://t.me/violex_official"

# ---------- لینک ربات ----------
BOT_LINK = "https://t.me/VIOLEXQ_bot?start="

# ---------- عکس درباره ما ----------
ABOUT_IMAGE_URL = "https://i.postimg.cc/Njj6HM7V/IMG-20260505-233450.jpg"

# ---------- مالک اصلی ----------
OWNER_ID = 7803165903

# ---------- گروه دبیران ----------
TEACHERS_GROUP_BIO = -1004360248131
TEACHERS_GROUP_CHEM = -1003961456151
TEACHERS_GROUP_PHYS = -1003554950675
TEACHERS_GROUP_MATH = -1004117472263

# ---------- گروه پشتیبانی ----------
SUPPORT_GROUP = -1003780590510

# ---------- گروه حسابداری ----------
ACCOUNTING_GROUP = -1003609493315

# ---------- کانال گزارش تراکنش ----------
TRANSACTION_CHANNEL = -1004348903892

# ---------- هدیه دعوت ----------
INVITE_REWARD = 4000
INVITE_REWARD_QUESTIONS = 3

# ---------- SMS.ir ----------
SMSIR_API_KEY = "B33h8avj7PGBquAGfOXPLOw7LKYnmJNBXIN9XuxJLrfK0ojd"
SMSIR_TEMPLATE_ID = 851804
SMSIR_LINE_NUMBER = "30004505000017"

# ---------- زیبال (غیرفعال موقت) ----------
ZIBAL_MERCHANT = os.environ.get("ZIBAL_MERCHANT", "69e3945ee6d570ad00fd0dad")
ZIBAL_SANDBOX = False
ZIBAL_ENABLED = False   # ⚠️ درگاه غیرفعال - بعد از رفع IP به True تغییر بده

RAILWAY_PUBLIC_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "your-app.up.railway.app")
ZIBAL_CALLBACK_URL = f"https://{RAILWAY_PUBLIC_DOMAIN}/zibal/callback"

# ---------- پورت وب‌سرور ----------
WEB_PORT = int(os.environ.get("PORT", 8080))

# ---------- تایم لیمیت‌ها ----------
TEACHER_TIMEOUT_MINUTES = 180
SUPPORT_TIMEOUT_HOURS = 24

# ---------- پکیج‌ها (مبلغ‌های درست - تومان) ----------
DEFAULT_PACKAGES = [
    {
        "id": 0,
        "name": "پکیج استارت",
        "price": 0,
        "days": 3,
        "questions": 4,
        "is_start": True,
    },
    {
        "id": 1,
        "name": "پکیج ۱ ماهه",
        "price": 250_000,
        "days": 30,
        "questions": 10,
        "is_start": False,
    },
    {
        "id": 2,
        "name": "پکیج ۲ ماهه + ۱ سوال هدیه",
        "price": 500_000,
        "days": 60,
        "questions": 21,
        "is_start": False,
    },
    {
        "id": 3,
        "name": "پکیج ۳ ماهه + ۳ سوال هدیه",
        "price": 750_000,
        "days": 90,
        "questions": 33,
        "is_start": False,
    },
    {
        "id": 4,
        "name": "پکیج ۴ ماهه + ۵ سوال هدیه",
        "price": 1_000_000,
        "days": 120,
        "questions": 45,
        "is_start": False,
    },
    {
        "id": 5,
        "name": "پکیج ۵ ماهه + ۶ سوال هدیه",
        "price": 1_250_000,
        "days": 150,
        "questions": 56,
        "is_start": False,
    },
    {
        "id": 6,
        "name": "پکیج ۶ ماهه + ۷ سوال هدیه",
        "price": 1_500_000,
        "days": 180,
        "questions": 67,
        "is_start": False,
    },
]

# ---------- نقش‌ها ----------
ROLE_OWNER = "owner"
ROLE_ADMIN = "admin"
ROLE_TEACHER = "teacher"
ROLE_ACCOUNTANT = "accountant"
ROLE_SUPPORT = "support"
ROLE_USER = "user"

# ---------- دروس ----------
SUBJECTS = {
    "زیست": {"emoji": "🧬", "prefix": "BIO", "group": TEACHERS_GROUP_BIO},
    "شیمی": {"emoji": "🧪", "prefix": "CHE", "group": TEACHERS_GROUP_CHEM},
    "فیزیک": {"emoji": "⚡️", "prefix": "PHY", "group": TEACHERS_GROUP_PHYS},
    "ریاضی": {"emoji": "📐", "prefix": "MATH", "group": TEACHERS_GROUP_MATH},
}