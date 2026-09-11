import os
import psycopg2
import psycopg2.extras
from datetime import datetime
import jdatetime


# ============================================
# اتصال به PostgreSQL
# ============================================

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    print("⚠️ هشدار: DATABASE_URL تنظیم نشده!")
    DATABASE_URL = None


def get_connection():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL تنظیم نشده است")
    url = DATABASE_URL
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    conn = psycopg2.connect(url)
    return conn


# ============================================
# راه‌اندازی دیتابیس
# ============================================

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            phone_verified INTEGER DEFAULT 0,
            verification_code TEXT,
            wallet BIGINT DEFAULT 0,
            questions_remaining INTEGER DEFAULT 0,
            questions_used INTEGER DEFAULT 0,
            active_package TEXT DEFAULT '0',
            package_expire_date TEXT DEFAULT '-',
            referrals INTEGER DEFAULT 0,
            invited_by BIGINT DEFAULT NULL,
            invited_by_rewarded INTEGER DEFAULT 0,
            has_start_package INTEGER DEFAULT 0,
            is_blocked INTEGER DEFAULT 0,
            role TEXT DEFAULT 'user',
            created_at TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            card_number TEXT,
            card_holder TEXT,
            photo_file_id TEXT,
            verified INTEGER DEFAULT 0,
            is_primary INTEGER DEFAULT 0,
            rejected_reason TEXT,
            created_at TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            subject TEXT,
            question_code TEXT UNIQUE,
            question_text TEXT,
            description TEXT,
            file_id TEXT,
            status TEXT DEFAULT 'waiting',
            teacher_id BIGINT DEFAULT NULL,
            teacher_username TEXT DEFAULT NULL,
            teacher_name TEXT DEFAULT NULL,
            teacher_display_name TEXT DEFAULT NULL,
            taken_time TEXT,
            timeout_time TEXT,
            answered_time TEXT,
            closed_time TEXT,
            teacher_invoice_counted INTEGER DEFAULT 1,
            created_at TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS question_replies (
            id SERIAL PRIMARY KEY,
            question_id INTEGER,
            teacher_id BIGINT,
            message_id BIGINT,
            content TEXT,
            file_id TEXT,
            created_at TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            amount BIGINT,
            card_number TEXT,
            transaction_id TEXT,
            status TEXT,
            type TEXT,
            created_at TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            ticket_code TEXT UNIQUE,
            message TEXT,
            status TEXT DEFAULT 'waiting',
            support_id BIGINT DEFAULT NULL,
            support_username TEXT DEFAULT NULL,
            support_name TEXT DEFAULT NULL,
            support_taken_time TEXT,
            timeout_time TEXT,
            reply TEXT,
            replied_time TEXT,
            closed_time TEXT,
            created_at TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS ticket_messages (
            id SERIAL PRIMARY KEY,
            ticket_id INTEGER,
            sender_type TEXT,
            sender_id BIGINT,
            message_id BIGINT,
            content TEXT,
            file_id TEXT,
            created_at TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS staff (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            username TEXT,
            display_name TEXT,
            role TEXT,
            subject TEXT,
            added_by BIGINT,
            created_at TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            authority TEXT UNIQUE,
            amount BIGINT,
            description TEXT,
            card_id INTEGER DEFAULT NULL,
            status TEXT DEFAULT 'pending',
            ref_id TEXT,
            card_pan TEXT,
            created_at TEXT,
            verified_at TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS discount_codes (
            id SERIAL PRIMARY KEY,
            code TEXT UNIQUE,
            percent INTEGER DEFAULT 0,
            amount BIGINT DEFAULT 0,
            max_uses INTEGER DEFAULT 0,
            used_count INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1,
            created_at TEXT
        )
    ''')

    conn.commit()
    c.close()
    conn.close()
    print("✅ دیتابیس PostgreSQL با موفقیت راه‌اندازی شد.")


# ============================================
# تاریخ شمسی
# ============================================

def get_shamsi_now():
    return jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")


def get_shamsi_date():
    return jdatetime.datetime.now().strftime("%Y/%m/%d")


def get_shamsi_future_date(days):
    future = jdatetime.datetime.now() + jdatetime.timedelta(days=days)
    return future.strftime("%Y/%m/%d")


# ============================================
# کاربران
# ============================================

def get_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = c.fetchone()
    c.close()
    conn.close()
    return user


def create_user(user_id, username, first_name, last_name, invited_by=None):
    conn = get_connection()
    c = conn.cursor()
    now = get_shamsi_now()

    c.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
    if c.fetchone():
        c.close()
        conn.close()
        return False

    c.execute('''
        INSERT INTO users
        (user_id, username, first_name, last_name, invited_by, created_at, package_expire_date)
        VALUES (%s, %s, %s, %s, %s, %s, '-')
    ''', (user_id, username, first_name, last_name, invited_by, now))
    conn.commit()
    c.close()
    conn.close()
    return True


def update_user(user_id, **kwargs):
    if not kwargs:
        return
    conn = get_connection()
    c = conn.cursor()
    for key, value in kwargs.items():
        c.execute(f"UPDATE users SET {key} = %s WHERE user_id = %s", (value, user_id))
    conn.commit()
    c.close()
    conn.close()


def reward_inviter(invited_user_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT invited_by, invited_by_rewarded FROM users WHERE user_id = %s", (invited_user_id,))
    row = c.fetchone()
    if not row:
        c.close()
        conn.close()
        return None

    inviter_id, already_rewarded = row
    if already_rewarded or not inviter_id:
        c.close()
        conn.close()
        return None

    c.execute("SELECT wallet, referrals, questions_remaining FROM users WHERE user_id = %s", (inviter_id,))
    inviter = c.fetchone()
    if not inviter:
        c.close()
        conn.close()
        return None

    from config import INVITE_REWARD, INVITE_REWARD_QUESTIONS

    c.execute('''
        UPDATE users
        SET wallet = %s, referrals = %s, questions_remaining = %s
        WHERE user_id = %s
    ''', (inviter[0] + INVITE_REWARD, inviter[1] + 1, inviter[2] + INVITE_REWARD_QUESTIONS, inviter_id))

    c.execute("UPDATE users SET invited_by_rewarded = 1 WHERE user_id = %s", (invited_user_id,))

    conn.commit()
    c.close()
    conn.close()
    return inviter_id


def get_all_users():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = [row[0] for row in c.fetchall()]
    c.close()
    conn.close()
    return users


def get_all_users_with_phone():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id, username, first_name, last_name, phone FROM users WHERE phone IS NOT NULL AND phone != ''")
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows


def get_user_role(user_id):
    from config import OWNER_ID
    if user_id == OWNER_ID:
        return "owner"
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT role FROM staff WHERE user_id = %s LIMIT 1", (user_id,))
    row = c.fetchone()
    c.close()
    conn.close()
    return row[0] if row else "user"


def is_staff(user_id, role=None):
    from config import OWNER_ID
    if user_id == OWNER_ID:
        return True
    conn = get_connection()
    c = conn.cursor()
    if role:
        c.execute("SELECT id FROM staff WHERE user_id = %s AND role = %s", (user_id, role))
    else:
        c.execute("SELECT id FROM staff WHERE user_id = %s", (user_id,))
    row = c.fetchone()
    c.close()
    conn.close()
    return row is not None


def add_staff(user_id, role, username=None, subject=None, added_by=None, display_name=None):
    conn = get_connection()
    c = conn.cursor()
    now = get_shamsi_now()
    c.execute('''
        INSERT INTO staff (user_id, username, display_name, role, subject, added_by, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (user_id, username, display_name, role, subject, added_by, now))
    conn.commit()
    c.close()
    conn.close()


def update_staff(user_id, role=None, **kwargs):
    if not kwargs:
        return
    conn = get_connection()
    c = conn.cursor()
    for key, value in kwargs.items():
        if role:
            c.execute(f"UPDATE staff SET {key} = %s WHERE user_id = %s AND role = %s", (value, user_id, role))
        else:
            c.execute(f"UPDATE staff SET {key} = %s WHERE user_id = %s", (value, user_id))
    conn.commit()
    c.close()
    conn.close()


def remove_staff(user_id, role=None):
    conn = get_connection()
    c = conn.cursor()
    if role:
        c.execute("DELETE FROM staff WHERE user_id = %s AND role = %s", (user_id, role))
    else:
        c.execute("DELETE FROM staff WHERE user_id = %s", (user_id,))
    conn.commit()
    c.close()
    conn.close()


def get_staff_list(role):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id, username, subject FROM staff WHERE role = %s", (role,))
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows


def get_staff_with_display_name(role):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id, username, display_name, subject FROM staff WHERE role = %s", (role,))
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows


def get_staff_by_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM staff WHERE user_id = %s", (user_id,))
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows


def staff_exists(user_id, role):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM staff WHERE user_id = %s AND role = %s", (user_id, role))
    row = c.fetchone()
    c.close()
    conn.close()
    return row is not None


def count_owners():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM staff WHERE role = 'owner'")
    count = c.fetchone()[0]
    c.close()
    conn.close()
    return count


# ============================================
# کد تأیید
# ============================================

def set_verification_code(user_id, code):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET verification_code = %s WHERE user_id = %s", (code, user_id))
    conn.commit()
    c.close()
    conn.close()


def get_verification_code(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT verification_code FROM users WHERE user_id = %s", (user_id,))
    row = c.fetchone()
    c.close()
    conn.close()
    return row[0] if row else None


# ============================================
# کارت
# ============================================

def add_card(user_id, card_number, card_holder, photo_file_id=None):
    conn = get_connection()
    c = conn.cursor()
    now = get_shamsi_now()

    c.execute("SELECT COUNT(*) FROM cards WHERE user_id = %s AND verified = 1", (user_id,))
    count = c.fetchone()[0]
    is_primary = 1 if count == 0 else 0

    c.execute('''
        INSERT INTO cards (user_id, card_number, card_holder, photo_file_id, is_primary, created_at)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
    ''', (user_id, card_number, card_holder, photo_file_id, is_primary, now))
    card_id = c.fetchone()[0]
    conn.commit()
    c.close()
    conn.close()
    return card_id


def get_user_cards(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM cards WHERE user_id = %s ORDER BY id DESC", (user_id,))
    cards = c.fetchall()
    c.close()
    conn.close()
    return cards


def get_verified_cards(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM cards WHERE user_id = %s AND verified = 1 ORDER BY is_primary DESC, id DESC", (user_id,))
    cards = c.fetchall()
    c.close()
    conn.close()
    return cards


def get_card(card_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM cards WHERE id = %s", (card_id,))
    card = c.fetchone()
    c.close()
    conn.close()
    return card


def verify_card(card_id, verified=True, reason=None):
    conn = get_connection()
    c = conn.cursor()
    if verified:
        c.execute("UPDATE cards SET verified = 1, rejected_reason = NULL WHERE id = %s", (card_id,))
    else:
        c.execute("UPDATE cards SET verified = 0, rejected_reason = %s WHERE id = %s", (reason, card_id))
    conn.commit()
    c.close()
    conn.close()


def delete_card(card_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM cards WHERE id = %s", (card_id,))
    conn.commit()
    c.close()
    conn.close()


# ============================================
# سوال
# ============================================

def generate_question_code(subject):
    from config import SUBJECTS
    prefix = SUBJECTS.get(subject, {}).get("prefix", "Q")
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM questions")
    count = c.fetchone()[0] + 1
    c.close()
    conn.close()
    return f"{prefix}-{count + 1000}"


def create_question(user_id, subject, question_text, description, file_id=None):
    conn = get_connection()
    c = conn.cursor()
    now = get_shamsi_now()
    code = generate_question_code(subject)
    c.execute('''
        INSERT INTO questions
        (user_id, subject, question_code, question_text, description, file_id, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
    ''', (user_id, subject, code, question_text, description, file_id, now))
    question_id = c.fetchone()[0]
    conn.commit()
    c.close()
    conn.close()
    return question_id, code


def get_question(question_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM questions WHERE id = %s", (question_id,))
    q = c.fetchone()
    c.close()
    conn.close()
    return q


def get_question_by_code(code):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM questions WHERE question_code = %s", (code,))
    q = c.fetchone()
    c.close()
    conn.close()
    return q


def update_question(question_id, **kwargs):
    if not kwargs:
        return
    conn = get_connection()
    c = conn.cursor()
    for key, value in kwargs.items():
        c.execute(f"UPDATE questions SET {key} = %s WHERE id = %s", (value, question_id))
    conn.commit()
    c.close()
    conn.close()


def get_waiting_questions(subject=None):
    conn = get_connection()
    c = conn.cursor()
    if subject:
        c.execute("SELECT * FROM questions WHERE status = 'waiting' AND subject = %s ORDER BY id", (subject,))
    else:
        c.execute("SELECT * FROM questions WHERE status = 'waiting' ORDER BY id")
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows


def get_teacher_active_question(teacher_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT id, question_code FROM questions
        WHERE teacher_id = %s AND status IN ('taken', 'answered')
        LIMIT 1
    ''', (teacher_id,))
    row = c.fetchone()
    c.close()
    conn.close()
    return row


def get_expired_questions():
    conn = get_connection()
    c = conn.cursor()
    now = get_shamsi_now()
    c.execute('''
        SELECT id, question_code, teacher_id
        FROM questions
        WHERE status = 'taken' AND timeout_time IS NOT NULL AND timeout_time < %s
    ''', (now,))
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows


# ============================================
# پاسخ دبیر
# ============================================

def add_question_reply(question_id, teacher_id, message_id, content, file_id=None):
    conn = get_connection()
    c = conn.cursor()
    now = get_shamsi_now()
    c.execute('''
        INSERT INTO question_replies (question_id, teacher_id, message_id, content, file_id, created_at)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
    ''', (question_id, teacher_id, message_id, content, file_id, now))
    reply_id = c.fetchone()[0]
    conn.commit()
    c.close()
    conn.close()
    return reply_id


# ============================================
# تیکت پشتیبانی
# ============================================

def generate_ticket_code():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM tickets")
    count = c.fetchone()[0] + 1
    c.close()
    conn.close()
    return f"SUP-{count + 1000}"


def create_ticket(user_id, message):
    conn = get_connection()
    c = conn.cursor()
    now = get_shamsi_now()
    code = generate_ticket_code()
    c.execute('''
        INSERT INTO tickets (user_id, ticket_code, message, created_at)
        VALUES (%s, %s, %s, %s) RETURNING id
    ''', (user_id, code, message, now))
    ticket_id = c.fetchone()[0]
    conn.commit()
    c.close()
    conn.close()
    return ticket_id, code


def get_ticket(ticket_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM tickets WHERE id = %s", (ticket_id,))
    t = c.fetchone()
    c.close()
    conn.close()
    return t


def get_user_open_ticket(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT id, ticket_code, status FROM tickets
        WHERE user_id = %s AND status IN ('waiting', 'taken', 'answered')
        ORDER BY id DESC LIMIT 1
    ''', (user_id,))
    row = c.fetchone()
    c.close()
    conn.close()
    return row


def get_open_ticket_for_support(support_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT id FROM tickets
        WHERE support_id = %s AND status IN ('taken', 'answered')
        LIMIT 1
    ''', (support_id,))
    row = c.fetchone()
    c.close()
    conn.close()
    return row[0] if row else None


def take_ticket(ticket_id, support_id, support_username, support_name):
    conn = get_connection()
    c = conn.cursor()
    now = get_shamsi_now()
    from config import SUPPORT_TIMEOUT_HOURS
    timeout = (jdatetime.datetime.now() + jdatetime.timedelta(hours=SUPPORT_TIMEOUT_HOURS)).strftime("%Y/%m/%d %H:%M:%S")
    c.execute('''
        UPDATE tickets
        SET status = 'taken',
            support_id = %s,
            support_username = %s,
            support_name = %s,
            support_taken_time = %s,
            timeout_time = %s
        WHERE id = %s
    ''', (support_id, support_username, support_name, now, timeout, ticket_id))
    conn.commit()
    c.close()
    conn.close()


def reply_ticket(ticket_id, reply, new_timeout_hours=24):
    conn = get_connection()
    c = conn.cursor()
    now = get_shamsi_now()
    timeout = (jdatetime.datetime.now() + jdatetime.timedelta(hours=new_timeout_hours)).strftime("%Y/%m/%d %H:%M:%S")
    c.execute('''
        UPDATE tickets
        SET reply = %s, status = 'answered', replied_time = %s, timeout_time = %s
        WHERE id = %s
    ''', (reply, now, timeout, ticket_id))
    conn.commit()
    c.close()
    conn.close()


def close_ticket(ticket_id):
    conn = get_connection()
    c = conn.cursor()
    now = get_shamsi_now()
    c.execute('''
        UPDATE tickets
        SET status = 'closed', closed_time = %s
        WHERE id = %s
    ''', (now, ticket_id))
    conn.commit()
    c.close()
    conn.close()


def get_expired_tickets():
    conn = get_connection()
    c = conn.cursor()
    now = get_shamsi_now()
    c.execute('''
        SELECT id, ticket_code FROM tickets
        WHERE status IN ('waiting', 'taken', 'answered')
          AND timeout_time IS NOT NULL
          AND timeout_time < %s
    ''', (now,))
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows


def add_ticket_message(ticket_id, sender_type, sender_id, message_id, content, file_id=None):
    conn = get_connection()
    c = conn.cursor()
    now = get_shamsi_now()
    c.execute('''
        INSERT INTO ticket_messages (ticket_id, sender_type, sender_id, message_id, content, file_id, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
    ''', (ticket_id, sender_type, sender_id, message_id, content, file_id, now))
    msg_id = c.fetchone()[0]
    conn.commit()
    c.close()
    conn.close()
    return msg_id


# ============================================
# تراکنش
# ============================================

def add_transaction(user_id, amount, card_number, transaction_id, status, type_):
    conn = get_connection()
    c = conn.cursor()
    now = get_shamsi_now()
    c.execute('''
        INSERT INTO transactions (user_id, amount, card_number, transaction_id, status, type, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (user_id, amount, card_number, transaction_id, status, type_, now))
    conn.commit()
    c.close()
    conn.close()


# ============================================
# پرداخت زیبال
# ============================================

def create_payment_record(user_id, authority, amount, description, card_id=None):
    conn = get_connection()
    c = conn.cursor()
    now = get_shamsi_now()
    c.execute('''
        INSERT INTO payments (user_id, authority, amount, description, card_id, created_at)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
    ''', (user_id, authority, amount, description, card_id, now))
    payment_id = c.fetchone()[0]
    conn.commit()
    c.close()
    conn.close()
    return payment_id


def get_payment_by_authority(authority):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM payments WHERE authority = %s", (authority,))
    p = c.fetchone()
    c.close()
    conn.close()
    return p


def update_payment_status(authority, status, ref_id=None, card_pan=None):
    conn = get_connection()
    c = conn.cursor()
    now = get_shamsi_now()
    if status == 'verified':
        c.execute('''
            UPDATE payments
            SET status = %s, ref_id = %s, card_pan = %s, verified_at = %s
            WHERE authority = %s
        ''', (status, ref_id, card_pan, now, authority))
    else:
        c.execute("UPDATE payments SET status = %s WHERE authority = %s", (status, authority))
    conn.commit()
    c.close()
    conn.close()


# ============================================
# آمار
# ============================================

def get_stats():
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM questions")
    total_questions = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM questions WHERE status = 'waiting'")
    waiting = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM questions WHERE status IN ('answered', 'closed')")
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

    c.close()
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


# ============================================
# آمار واقعی بر اساس تاریخ
# ============================================

def get_users_stats():
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]

    now = jdatetime.datetime.now()
    today_str = now.strftime("%Y/%m/%d")
    week_ago = (now - jdatetime.timedelta(days=7)).strftime("%Y/%m/%d")
    month_ago = (now - jdatetime.timedelta(days=30)).strftime("%Y/%m/%d")

    c.execute("SELECT COUNT(*) FROM users WHERE created_at LIKE %s", (f"{today_str}%",))
    today = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users WHERE created_at >= %s", (week_ago,))
    week = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users WHERE created_at >= %s", (month_ago,))
    month = c.fetchone()[0]

    c.close()
    conn.close()

    return {'total': total, 'today': today, 'week': week, 'month': month}


def get_questions_stats():
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM questions")
    total = c.fetchone()[0]

    now = jdatetime.datetime.now()
    today_str = now.strftime("%Y/%m/%d")
    week_ago = (now - jdatetime.timedelta(days=7)).strftime("%Y/%m/%d")
    month_ago = (now - jdatetime.timedelta(days=30)).strftime("%Y/%m/%d")

    c.execute("SELECT COUNT(*) FROM questions WHERE created_at LIKE %s", (f"{today_str}%",))
    today = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM questions WHERE created_at >= %s", (week_ago,))
    week = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM questions WHERE created_at >= %s", (month_ago,))
    month = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM questions WHERE subject = 'زیست'")
    bio = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM questions WHERE subject = 'شیمی'")
    chem = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM questions WHERE subject = 'فیزیک'")
    phys = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM questions WHERE subject = 'ریاضی'")
    math = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM questions WHERE status IN ('answered', 'closed')")
    answered = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM questions WHERE status = 'waiting'")
    waiting = c.fetchone()[0]

    c.close()
    conn.close()

    return {
        'total': total, 'today': today, 'week': week, 'month': month,
        'bio': bio, 'chem': chem, 'phys': phys, 'math': math,
        'answered': answered, 'waiting': waiting,
    }


def get_income_stats():
    conn = get_connection()
    c = conn.cursor()

    now = jdatetime.datetime.now()
    today_str = now.strftime("%Y/%m/%d")
    week_ago = (now - jdatetime.timedelta(days=7)).strftime("%Y/%m/%d")
    month_ago = (now - jdatetime.timedelta(days=30)).strftime("%Y/%m/%d")

    c.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE status = 'success' AND created_at LIKE %s", (f"{today_str}%",))
    today = c.fetchone()[0]

    c.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE status = 'success' AND created_at >= %s", (week_ago,))
    week = c.fetchone()[0]

    c.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE status = 'success' AND created_at >= %s", (month_ago,))
    month = c.fetchone()[0]

    c.close()
    conn.close()

    return {'today': today, 'week': week, 'month': month}


# ============================================
# صورت‌حساب دبیران
# ============================================

def get_teacher_invoice_detail(teacher_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute('''
        SELECT COUNT(*) FROM questions
        WHERE teacher_id = %s AND status IN ('answered', 'closed')
    ''', (teacher_id,))
    total = c.fetchone()[0]

    today_str = get_shamsi_date()
    c.execute('''
        SELECT COUNT(*) FROM questions
        WHERE teacher_id = %s AND status IN ('answered', 'closed')
        AND answered_time LIKE %s
    ''', (teacher_id, f"{today_str}%"))
    today = c.fetchone()[0]

    now = jdatetime.datetime.now()
    week_ago = (now - jdatetime.timedelta(days=7)).strftime("%Y/%m/%d")
    c.execute('''
        SELECT COUNT(*) FROM questions
        WHERE teacher_id = %s AND status IN ('answered', 'closed')
        AND answered_time >= %s
    ''', (teacher_id, week_ago))
    week = c.fetchone()[0]

    month_ago = (now - jdatetime.timedelta(days=30)).strftime("%Y/%m/%d")
    c.execute('''
        SELECT COUNT(*) FROM questions
        WHERE teacher_id = %s AND status IN ('answered', 'closed')
        AND answered_time >= %s
    ''', (teacher_id, month_ago))
    month = c.fetchone()[0]

    c.close()
    conn.close()

    return {'total': total, 'today': today, 'week': week, 'month': month}


def get_teachers_invoice_full():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id, username, display_name, subject FROM staff WHERE role = 'teacher'")
    teachers = c.fetchall()
    c.close()
    conn.close()

    result = []
    for tid, uname, dname, subj in teachers:
        detail = get_teacher_invoice_detail(tid)
        result.append({
            'teacher_id': tid,
            'username': uname,
            'display_name': dname or uname or str(tid),
            'subject': subj or 'نامشخص',
            'total_questions': detail['total'],
            'today_questions': detail['today'],
            'week_questions': detail['week'],
            'month_questions': detail['month'],
        })

    return result


def reset_teacher_invoice():
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE questions SET teacher_invoice_counted = 0 WHERE teacher_invoice_counted = 1")
    conn.commit()
    c.close()
    conn.close()


# ============================================
# کاربران فعال / خریداران / شماره‌ها
# ============================================

def get_active_users(days=30):
    conn = get_connection()
    c = conn.cursor()
    now = jdatetime.datetime.now()
    cutoff = (now - jdatetime.timedelta(days=days)).strftime("%Y/%m/%d")
    c.execute("SELECT DISTINCT user_id FROM questions WHERE created_at >= %s", (cutoff,))
    users = [row[0] for row in c.fetchall()]
    c.close()
    conn.close()
    return users


def get_package_buyers():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT DISTINCT user_id FROM transactions WHERE type = 'package' AND status = 'success'")
    users = [row[0] for row in c.fetchall()]
    c.close()
    conn.close()
    return users


def get_user_purchases(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT id, amount, type, status, created_at 
        FROM transactions 
        WHERE user_id = %s 
        ORDER BY id DESC 
        LIMIT 20
    ''', (user_id,))
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows


def export_phone_list():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT user_id, username, first_name, last_name, phone, created_at
        FROM users 
        WHERE phone IS NOT NULL AND phone != ''
        ORDER BY user_id
    ''')
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows


def get_total_phones_count():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users WHERE phone IS NOT NULL AND phone != ''")
    count = c.fetchone()[0]
    c.close()
    conn.close()
    return count


# ============================================
# کد تخفیف
# ============================================

def create_discount_code(code, percent=0, amount=0, max_uses=0):
    conn = get_connection()
    c = conn.cursor()
    now = get_shamsi_now()
    try:
        c.execute('''
            INSERT INTO discount_codes (code, percent, amount, max_uses, created_at)
            VALUES (%s, %s, %s, %s, %s)
        ''', (code, percent, amount, max_uses, now))
        conn.commit()
        return True
    except:
        return False
    finally:
        c.close()
        conn.close()


def get_discount_code(code):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM discount_codes WHERE code = %s AND active = 1", (code,))
    row = c.fetchone()
    c.close()
    conn.close()
    return row


def use_discount_code(code):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE discount_codes SET used_count = used_count + 1 WHERE code = %s", (code,))
    conn.commit()
    c.close()
    conn.close()