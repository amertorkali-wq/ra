import sqlite3
from datetime import datetime
import jdatetime

DB_NAME = "violex.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # جدول کاربران
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            verification_code TEXT,
            wallet INTEGER DEFAULT 0,
            questions_remaining INTEGER DEFAULT 0,
            questions_used INTEGER DEFAULT 0,
            active_package TEXT DEFAULT '0',
            package_expire_date TEXT DEFAULT '-',
            referrals INTEGER DEFAULT 0,
            invited_by INTEGER DEFAULT NULL,
            invited_by_rewarded INTEGER DEFAULT 0,
            has_start_package INTEGER DEFAULT 0,
            is_blocked INTEGER DEFAULT 0,
            role TEXT DEFAULT 'user',
            created_at TEXT
        )
    ''')

    # جدول کارت‌ها
    c.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            card_number TEXT,
            card_holder TEXT,
            photo_file_id TEXT,
            verified INTEGER DEFAULT 0,
            rejected_reason TEXT,
            created_at TEXT
        )
    ''')

    # جدول سوالات
    c.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            subject TEXT,
            question_code TEXT UNIQUE,
            question_text TEXT,
            description TEXT,
            file_id TEXT,
            status TEXT DEFAULT 'waiting',
            teacher_id INTEGER DEFAULT NULL,
            taken_time TEXT,
            closed_time TEXT,
            created_at TEXT
        )
    ''')

    # جدول تراکنش‌ها
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            card_number TEXT,
            transaction_id TEXT,
            status TEXT,
            type TEXT,
            created_at TEXT
        )
    ''')

    # جدول تیکت‌ها
    c.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            ticket_code TEXT UNIQUE,
            message TEXT,
            status TEXT DEFAULT 'open',
            reply TEXT,
            created_at TEXT
        )
    ''')

    # جدول کارکنان
    c.execute('''
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            role TEXT,
            subject TEXT,
            added_by INTEGER,
            created_at TEXT
        )
    ''')

    # جدول تنظیمات
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ دیتابیس با موفقیت راه‌اندازی شد.")


# ============================================
# توابع تاریخ شمسی
# ============================================

def get_shamsi_now():
    now = jdatetime.datetime.now()
    return now.strftime("%Y/%m/%d %H:%M:%S")


def get_shamsi_date():
    now = jdatetime.datetime.now()
    return now.strftime("%Y/%m/%d")


def get_shamsi_future_date(days):
    future = jdatetime.datetime.now() + jdatetime.timedelta(days=days)
    return future.strftime("%Y/%m/%d")


# ============================================
# توابع کاربر
# ============================================

def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user


def create_user(user_id, username, first_name, last_name, invited_by=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = get_shamsi_now()

    c.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if c.fetchone():
        conn.close()
        return False

    c.execute('''
        INSERT INTO users
        (user_id, username, first_name, last_name, invited_by, created_at, package_expire_date)
        VALUES (?, ?, ?, ?, ?, ?, '-')
    ''', (user_id, username, first_name, last_name, invited_by, now))
    conn.commit()
    conn.close()
    return True


def update_user(user_id, **kwargs):
    if not kwargs:
        return
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for key, value in kwargs.items():
        c.execute(f"UPDATE users SET {key} = ? WHERE user_id = ?", (value, user_id))
    conn.commit()
    conn.close()


def reward_inviter(invited_user_id):
    """پاداش به دعوت‌کننده بعد از عضویت در کانال"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT invited_by, invited_by_rewarded FROM users WHERE user_id = ?", (invited_user_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None

    inviter_id, already_rewarded = row

    if already_rewarded or not inviter_id:
        conn.close()
        return None

    c.execute("SELECT wallet, referrals, questions_remaining FROM users WHERE user_id = ?", (inviter_id,))
    inviter = c.fetchone()
    if not inviter:
        conn.close()
        return None

    from config import INVITE_REWARD, INVITE_REWARD_QUESTIONS

    new_wallet = inviter[0] + INVITE_REWARD
    new_referrals = inviter[1] + 1
    new_questions = inviter[2] + INVITE_REWARD_QUESTIONS

    c.execute('''
        UPDATE users
        SET wallet = ?, referrals = ?, questions_remaining = ?
        WHERE user_id = ?
    ''', (new_wallet, new_referrals, new_questions, inviter_id))

    c.execute("UPDATE users SET invited_by_rewarded = 1 WHERE user_id = ?", (invited_user_id,))

    conn.commit()
    conn.close()
    return inviter_id


def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users


def get_user_role(user_id):
    from config import OWNER_ID
    if user_id == OWNER_ID:
        return "owner"
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT role FROM staff WHERE user_id = ? LIMIT 1", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else "user"


def is_staff(user_id, role=None):
    from config import OWNER_ID
    if user_id == OWNER_ID:
        return True
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if role:
        c.execute("SELECT id FROM staff WHERE user_id = ? AND role = ?", (user_id, role))
    else:
        c.execute("SELECT id FROM staff WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row is not None


def add_staff(user_id, role, subject=None, added_by=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = get_shamsi_now()
    c.execute('''
        INSERT INTO staff (user_id, role, subject, added_by, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, role, subject, added_by, now))
    conn.commit()
    conn.close()


def remove_staff(user_id, role=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if role:
        c.execute("DELETE FROM staff WHERE user_id = ? AND role = ?", (user_id, role))
    else:
        c.execute("DELETE FROM staff WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def get_staff_list(role):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id, subject FROM staff WHERE role = ?", (role,))
    rows = c.fetchall()
    conn.close()
    return rows


# ============================================
# توابع کد تأیید
# ============================================

def set_verification_code(user_id, code):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET verification_code = ? WHERE user_id = ?", (code, user_id))
    conn.commit()
    conn.close()


def get_verification_code(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT verification_code FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


# ============================================
# توابع کارت
# ============================================

def add_card(user_id, card_number, card_holder, photo_file_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = get_shamsi_now()
    c.execute('''
        INSERT INTO cards (user_id, card_number, card_holder, photo_file_id, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, card_number, card_holder, photo_file_id, now))
    card_id = c.lastrowid
    conn.commit()
    conn.close()
    return card_id


def get_user_cards(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM cards WHERE user_id = ? ORDER BY id DESC", (user_id,))
    cards = c.fetchall()
    conn.close()
    return cards


def get_verified_cards(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM cards WHERE user_id = ? AND verified = 1", (user_id,))
    cards = c.fetchall()
    conn.close()
    return cards


def get_card(card_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM cards WHERE id = ?", (card_id,))
    card = c.fetchone()
    conn.close()
    return card


def verify_card(card_id, verified=True, reason=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if verified:
        c.execute("UPDATE cards SET verified = 1, rejected_reason = NULL WHERE id = ?", (card_id,))
    else:
        c.execute("UPDATE cards SET verified = 0, rejected_reason = ? WHERE id = ?", (reason, card_id))
    conn.commit()
    conn.close()


def delete_card(card_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM cards WHERE id = ?", (card_id,))
    conn.commit()
    conn.close()


# ============================================
# توابع سوال
# ============================================

def generate_question_code(subject):
    from config import SUBJECTS
    prefix = SUBJECTS.get(subject, {}).get("prefix", "Q")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM questions")
    count = c.fetchone()[0] + 1
    conn.close()
    return f"{prefix}-{count + 1000}"


def create_question(user_id, subject, question_text, description, file_id=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = get_shamsi_now()
    code = generate_question_code(subject)
    c.execute('''
        INSERT INTO questions
        (user_id, subject, question_code, question_text, description, file_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, subject, code, question_text, description, file_id, now))
    question_id = c.lastrowid
    conn.commit()
    conn.close()
    return question_id, code


def get_question(question_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
    q = c.fetchone()
    conn.close()
    return q


def get_question_by_code(code):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM questions WHERE question_code = ?", (code,))
    q = c.fetchone()
    conn.close()
    return q


def update_question(question_id, **kwargs):
    if not kwargs:
        return
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for key, value in kwargs.items():
        c.execute(f"UPDATE questions SET {key} = ? WHERE id = ?", (value, question_id))
    conn.commit()
    conn.close()


def get_waiting_questions(subject=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if subject:
        c.execute("SELECT * FROM questions WHERE status = 'waiting' AND subject = ? ORDER BY id", (subject,))
    else:
        c.execute("SELECT * FROM questions WHERE status = 'waiting' ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return rows


# ============================================
# توابع تیکت
# ============================================

def generate_ticket_code():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM tickets")
    count = c.fetchone()[0] + 1
    conn.close()
    return f"SUP-{count + 1000}"


def create_ticket(user_id, message):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = get_shamsi_now()
    code = generate_ticket_code()
    c.execute('''
        INSERT INTO tickets (user_id, ticket_code, message, created_at)
        VALUES (?, ?, ?, ?)
    ''', (user_id, code, message, now))
    ticket_id = c.lastrowid
    conn.commit()
    conn.close()
    return ticket_id, code


def get_ticket(ticket_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    t = c.fetchone()
    conn.close()
    return t


def reply_ticket(ticket_id, reply):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE tickets SET reply = ?, status = 'answered' WHERE id = ?", (reply, ticket_id))
    conn.commit()
    conn.close()


# ============================================
# تراکنش
# ============================================

def add_transaction(user_id, amount, card_number, transaction_id, status, type_):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    now = get_shamsi_now()
    c.execute('''
        INSERT INTO transactions (user_id, amount, card_number, transaction_id, status, type, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, amount, card_number, transaction_id, status, type_, now))
    conn.commit()
    conn.close()


# ============================================
# آمار
# ============================================

def get_stats():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM questions")
    total_questions = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM questions WHERE status = 'waiting'")
    waiting = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM questions WHERE status = 'answered'")
    answered = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM questions WHERE subject = 'زیست'")
    bio = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM questions WHERE subject = 'شیمی'")
    chem = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM questions WHERE subject = 'فیزیک'")
    phys = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM questions WHERE subject = 'ریاضی'")
    math = c.fetchone()[0]

    c.execute("SELECT SUM(amount) FROM transactions WHERE status = 'success'")
    income = c.fetchone()[0] or 0

    conn.close()

    return {
        'total_users': total_users,
        'total_questions': total_questions,
        'waiting': waiting,
        'answered': answered,
        'bio': bio,
        'chem': chem,
        'phys': phys,
        'math': math,
        'income': income,
    }