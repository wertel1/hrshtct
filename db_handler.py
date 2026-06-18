import sqlite3
from datetime import datetime, timedelta
from config import DB_NAME

def get_db():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, remind_hour INTEGER DEFAULT 21)")
    cur.execute("CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, date TEXT, mood INTEGER, work REAL, sleep REAL, comment TEXT, UNIQUE(user_id, date))")
    conn.commit()
    conn.close()

def save_user(user_id, username, first_name):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO users (user_id, username, first_name) VALUES (?,?,?)", (user_id, username, first_name))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return cur.fetchone()

def update_remind(user_id, hour):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET remind_hour = ? WHERE user_id = ?", (hour, user_id))
    conn.commit()
    conn.close()

def save_record(user_id, mood, work, sleep, comment):
    conn = get_db()
    cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("INSERT OR REPLACE INTO records (user_id, date, mood, work, sleep, comment) VALUES (?,?,?,?,?,?)", (user_id, today, mood, work, sleep, comment))
    conn.commit()
    conn.close()

def get_today(user_id):
    conn = get_db()
    cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("SELECT 1 FROM records WHERE user_id = ? AND date = ?", (user_id, today))
    return cur.fetchone() is not None

def get_records(user_id, days=30):
    conn = get_db()
    cur = conn.cursor()
    date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    cur.execute("SELECT date, mood, work, sleep, comment FROM records WHERE user_id = ? AND date >= ? ORDER BY date DESC", (user_id, date_from))
    return cur.fetchall()

def get_stats(user_id, days=7):
    conn = get_db()
    cur = conn.cursor()
    date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    cur.execute("SELECT COUNT(*), ROUND(AVG(mood),1), MAX(mood), MIN(mood), ROUND(AVG(work),1), ROUND(AVG(sleep),1) FROM records WHERE user_id = ? AND date >= ?", (user_id, date_from))
    return cur.fetchone()

def clear_data(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM records WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT user_id, remind_hour FROM users")
    return cur.fetchall()