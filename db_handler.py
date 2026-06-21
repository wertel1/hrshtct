import sqlite3
from datetime import datetime

def get_db():
    return sqlite3.connect('mood_tracker.db', check_same_thread=False)

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            mood INTEGER,
            hours_work REAL,
            hours_sleep REAL,
            comment TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_entry(user_id, mood, hours_work, hours_sleep, comment):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO entries (user_id, date, mood, hours_work, hours_sleep, comment)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, datetime.now().strftime('%Y-%m-%d'), mood, hours_work, hours_sleep, comment))
    conn.commit()
    conn.close()

def get_entries(user_id, limit=30):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT date, mood, hours_work, hours_sleep, comment
        FROM entries
        WHERE user_id = ?
        ORDER BY date DESC
        LIMIT ?
    ''', (user_id, limit))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_all_entries(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT date, mood, hours_work, hours_sleep
        FROM entries
        WHERE user_id = ?
        ORDER BY date
    ''', (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def clear_user_data(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM entries WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_stats(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT COUNT(*), AVG(mood), AVG(hours_work), AVG(hours_sleep)
        FROM entries
        WHERE user_id = ?
    ''', (user_id,))
    rows = cur.fetchone()
    conn.close()
    return rows

init_db()