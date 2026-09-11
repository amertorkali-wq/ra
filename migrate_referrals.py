from database import get_connection

conn = get_connection()
c = conn.cursor()

c.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_status TEXT DEFAULT 'pending'")
c.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_completed_at TEXT DEFAULT NULL")

conn.commit()
c.close()
conn.close()

print("? Migration ?? ?????? ????? ??!")
