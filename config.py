# ============================================
# تنظیمات ربات VIOLEX
# ============================================

TOKEN = "8762301184:AAGbn9CZirNf7Yc9nRdnBpQMfFGEnu8r9wA"

# کانال جوین اجباری
CHANNEL_ID = -1003858232624
CHANNEL_LINK = "https://t.me/violex_official"

# لینک ربات تلگرام
BOT_LINK = "https://t.me/VIOLEXQ_bot?start="

# لینک عکس درباره ما
ABOUT_IMAGE_URL = None

# مالک اصلی
OWNER_ID = 7803165903

# گروه دبیران
TEACHERS_GROUP_BIO = -1004360248131
TEACHERS_GROUP_CHEM = -1003961456151
TEACHERS_GROUP_PHYS = -1003554950675
TEACHERS_GROUP_MATH = -1004117472263

# گروه پشتیبانی
SUPPORT_GROUP = -1003780590510

# کانال گزارش تراکنش‌ها
TRANSACTION_CHANNEL = -1004348903892

# گروه حسابداری
ACCOUNTING_GROUP = -1003780590510

# هدیه دعوت
INVITE_REWARD = 4000
INVITE_REWARD_QUESTIONS = 3

# ---------- تنظیمات SMS.ir ----------
SMSIR_API_KEY = "B33h8avj7PGBquAGfOXPLOw7LKYnmJNBXIN9XuxJLrfK0ojd"
SMSIR_TEMPLATE_ID = 851804  # ✅ شناسه قالب صحیح
SMSIR_LINE_NUMBER = "30004505000017"

# درگاه پرداخت
ZARINPAL_MERCHANT = None

# پکیج‌ها
DEFAULT_PACKAGES = [
    {"id": 0, "name": "پکیج استارت", "price": 0, "days": 3, "questions": 4, "is_start": True},
    {"id": 1, "name": "پکیج 1 ماهه", "price": 250000, "days": 30, "questions": 10, "is_start": False},
    {"id": 2, "name": "پکیج 2 ماهه + 1 سوال هدیه", "price": 500000, "days": 60, "questions": 21, "is_start": False},
    {"id": 3, "name": "پکیج 3 ماهه + 3 سوال هدیه", "price": 750000, "days": 90, "questions": 33, "is_start": False},
    {"id": 4, "name": "پکیج 4 ماهه + 5 سوال هدیه", "price": 1000000, "days": 120, "questions": 45, "is_start": False},
    {"id": 5, "name": "پکیج 5 ماهه + 6 سوال هدیه", "price": 1250000, "days": 150, "questions": 56, "is_start": False},
    {"id": 6, "name": "پکیج 6 ماهه + 7 سوال هدیه", "price": 1500000, "days": 180, "questions": 67, "is_start": False},
]

# نقش‌ها
ROLE_OWNER = "owner"
ROLE_ADMIN = "admin"
ROLE_TEACHER = "teacher"
ROLE_ACCOUNTANT = "accountant"
ROLE_SUPPORT = "support"
ROLE_USER = "user"

# دروس
SUBJECTS = {
    "زیست": {"emoji": "🧬", "prefix": "BIO", "group": TEACHERS_GROUP_BIO},
    "شیمی": {"emoji": "🧪", "prefix": "CHE", "group": TEACHERS_GROUP_CHEM},
    "فیزیک": {"emoji": "⚡️", "prefix": "PHY", "group": TEACHERS_GROUP_PHYS},
    "ریاضی": {"emoji": "📐", "prefix": "MATH", "group": TEACHERS_GROUP_MATH},
}