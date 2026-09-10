import os

# ============================================
# تنظیمات ربات VIOLEX
# ============================================

TOKEN = "8762301184:AAGbn9CZirNf7Yc9nRdnBpQMfFGEnu8r9wA"

CHANNEL_ID = -1003858232624
CHANNEL_LINK = "https://t.me/violex_official"
BOT_LINK = "https://t.me/VIOLEXQ_bot?start="

ABOUT_IMAGE_URL = "https://i.postimg.cc/Njj6HM7V/IMG-20260505-233450.jpg"

OWNER_ID = 7803165903

TEACHERS_GROUP_BIO = -1004360248131
TEACHERS_GROUP_CHEM = -1003961456151
TEACHERS_GROUP_PHYS = -1003554950675
TEACHERS_GROUP_MATH = -1004117472263

SUPPORT_GROUP = -1003780590510
ACCOUNTING_GROUP = -1003609493315
TRANSACTION_CHANNEL = -1004348903892

INVITE_REWARD = 4000
INVITE_REWARD_QUESTIONS = 3

SMSIR_API_KEY = "B33h8avj7PGBquAGfOXPLOw7LKYnmJNBXIN9XuxJLrfK0ojd"
SMSIR_TEMPLATE_ID = 851804
SMSIR_LINE_NUMBER = "30004505000017"

# ---------- تنظیمات زیبال ----------
# ⚠️ در حالت تست از کد "zibal" استفاده می‌شود
# بعد از پیدا کردن Merchant ID اصلی، این را جایگزین کنید
ZIBAL_MERCHANT = os.environ.get("ZIBAL_MERCHANT", "zibal")
ZIBAL_SANDBOX = True

TEACHER_TIMEOUT_MINUTES = 180
SUPPORT_TIMEOUT_HOURS = 24

DEFAULT_PACKAGES = [
    {"id": 0, "name": "پکیج استارت", "price": 0, "days": 3, "questions": 4, "is_start": True},
    {"id": 1, "name": "پکیج 1 ماهه", "price": 250000, "days": 30, "questions": 10, "is_start": False},
    {"id": 2, "name": "پکیج 2 ماهه + 1 سوال هدیه", "price": 500000, "days": 60, "questions": 21, "is_start": False},
    {"id": 3, "name": "پکیج 3 ماهه + 3 سوال هدیه", "price": 750000, "days": 90, "questions": 33, "is_start": False},
    {"id": 4, "name": "پکیج 4 ماهه + 5 سوال هدیه", "price": 1000000, "days": 120, "questions": 45, "is_start": False},
    {"id": 5, "name": "پکیج 5 ماهه + 6 سوال هدیه", "price": 1250000, "days": 150, "questions": 56, "is_start": False},
    {"id": 6, "name": "پکیج 6 ماهه + 7 سوال هدیه", "price": 1500000, "days": 180, "questions": 67, "is_start": False},
]

ROLE_OWNER = "owner"
ROLE_ADMIN = "admin"
ROLE_TEACHER = "teacher"
ROLE_ACCOUNTANT = "accountant"
ROLE_SUPPORT = "support"
ROLE_USER = "user"

SUBJECTS = {
    "زیست": {"emoji": "🧬", "prefix": "BIO", "group": TEACHERS_GROUP_BIO},
    "شیمی": {"emoji": "🧪", "prefix": "CHE", "group": TEACHERS_GROUP_CHEM},
    "فیزیک": {"emoji": "⚡️", "prefix": "PHY", "group": TEACHERS_GROUP_PHYS},
    "ریاضی": {"emoji": "📐", "prefix": "MATH", "group": TEACHERS_GROUP_MATH},
}