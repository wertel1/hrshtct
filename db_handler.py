import sqlite3
from datetime import datetime, timedelta

from config import DB_NAME

def get_db():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            remind_hour INTEGER DEFAULT 21
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            record_date TEXT,
            mood INTEGER CHECK (mood BETWEEN 1 AND 5),
            work_hours REAL CHECK (work_hours >= 0),
            sleep_hours REAL CHECK (sleep_hours >= 0),
            comment TEXT,
            UNIQUE(user_id, record_date)
        )
    """)
    conn.commit()
    conn.close()

def save_user(user_id, username, first_name):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
                (user_id, username, first_name))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()
    conn.close()
    return result

def update_remind_hour(user_id, hour):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET remind_hour = ? WHERE user_id = ?", (hour, user_id))
    conn.commit()
    conn.close()

def save_record(user_id, mood, work_hours, sleep_hours, comment):
    conn = get_db()
    cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("""
        INSERT OR REPLACE INTO daily_records (user_id, record_date, mood, work_hours, sleep_hours, comment)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, today, mood, work_hours, sleep_hours, comment))
    conn.commit()
    conn.close()

def record_exists_today(user_id):
    conn = get_db()
    cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("SELECT 1 FROM daily_records WHERE user_id = ? AND record_date = ?", (user_id, today))
    result = cur.fetchone()
    conn.close()
    return result is not None

def get_records(user_id, days=7):
    conn = get_db()
    cur = conn.cursor()
    date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    cur.execute("""
        SELECT record_date, mood, work_hours, sleep_hours, comment
        FROM daily_records
        WHERE user_id = ? AND record_date >= ?
        ORDER BY record_date DESC
    """, (user_id, date_from))
    result = cur.fetchall()
    conn.close()
    return result

def get_stats(user_id, days=7):
    conn = get_db()
    cur = conn.cursor()
    date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    cur.execute("""
        SELECT
            COUNT(*) as total,
            ROUND(AVG(mood), 1) as avg_mood,
            MAX(mood) as max_mood,
            MIN(mood) as min_mood,
            ROUND(AVG(work_hours), 1) as avg_work,
            MAX(work_hours) as max_work,
            ROUND(AVG(sleep_hours), 1) as avg_sleep,
            MAX(sleep_hours) as max_sleep,
            MIN(sleep_hours) as min_sleep
        FROM daily_records
        WHERE user_id = ? AND record_date >= ?
    """, (user_id, date_from))
    result = cur.fetchone()
    conn.close()
    return result

def clear_user_data(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM daily_records WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_sleep_correlation(user_id):
    conn = get_db()
    cur = conn.cursor()
    date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    cur.execute("""
        SELECT 
            CASE 
                WHEN sleep_hours < 6 THEN '<6ч'
                WHEN sleep_hours < 7 THEN '6-7ч'
                WHEN sleep_hours < 8 THEN '7-8ч'
                WHEN sleep_hours < 9 THEN '8-9ч'
                ELSE '>9ч'
            END as sleep_range,
            ROUND(AVG(mood), 1) as avg_mood,
            COUNT(*) as count
        FROM daily_records
        WHERE user_id = ? AND record_date >= ?
        GROUP BY sleep_range
        ORDER BY MIN(sleep_hours)
    """, (user_id, date_from))
    result = cur.fetchall()
    conn.close()
    return result

def get_work_correlation(user_id):
    conn = get_db()
    cur = conn.cursor()
    date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    cur.execute("""
        SELECT 
            CASE 
                WHEN work_hours < 2 THEN '<2ч'
                WHEN work_hours < 4 THEN '2-4ч'
                WHEN work_hours < 6 THEN '4-6ч'
                WHEN work_hours < 8 THEN '6-8ч'
                ELSE '>8ч'
            END as work_range,
            ROUND(AVG(mood), 1) as avg_mood,
            COUNT(*) as count
        FROM daily_records
        WHERE user_id = ? AND record_date >= ?
        GROUP BY work_range
        ORDER BY MIN(work_hours)
    """, (user_id, date_from))
    result = cur.fetchall()
    conn.close()
    return result

def get_all_users():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT user_id, remind_hour FROM users")
    result = cur.fetchall()
    conn.close()
    return result

def get_best_worst_days(user_id):
    conn = get_db()
    cur = conn.cursor()
    date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    cur.execute("""
        SELECT record_date, mood, work_hours, sleep_hours, comment
        FROM daily_records
        WHERE user_id = ? AND record_date >= ?
        ORDER BY mood DESC, sleep_hours DESC
        LIMIT 1
    """, (user_id, date_from))
    best = cur.fetchone()
    cur.execute("""
        SELECT record_date, mood, work_hours, sleep_hours, comment
        FROM daily_records
        WHERE user_id = ? AND record_date >= ?
        ORDER BY mood ASC, sleep_hours ASC
        LIMIT 1
    """, (user_id, date_from))
    worst = cur.fetchone()
    conn.close()
    return best, worst

def get_weekday_stats(user_id):
    conn = get_db()
    cur = conn.cursor()
    date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    cur.execute("""
        SELECT 
            strftime('%w', record_date) as weekday,
            ROUND(AVG(mood), 1) as avg_mood,
            COUNT(*) as count
        FROM daily_records
        WHERE user_id = ? AND record_date >= ?
        GROUP BY weekday
        ORDER BY weekday
    """, (user_id, date_from))
    result = cur.fetchall()
    conn.close()
    return result

def get_history(user_id, days):
    conn = get_db()
    cur = conn.cursor()
    date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    cur.execute("""
        SELECT record_date, mood, work_hours, sleep_hours, comment
        FROM daily_records
        WHERE user_id = ? AND record_date >= ?
        ORDER BY record_date DESC
    """, (user_id, date_from))
    result = cur.fetchall()
    conn.close()
    return result