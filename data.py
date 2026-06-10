
import sqlite3
from datetime import datetime, timedelta
from config import DB_NAME

MY_USER_ID = 123456789  

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()


cur.execute("SELECT 1 FROM users WHERE user_id = ?", (MY_USER_ID,))
if not cur.fetchone():
    cur.execute("INSERT INTO users (user_id, username, first_name, remind_hour) VALUES (?, ?, ?, ?)",
                (MY_USER_ID, "test_user", "Тестовый", 21))

cur.execute("DELETE FROM daily_records WHERE user_id = ?", (MY_USER_ID,))


test_data = [
    (0, 4, 6.0, 7.5, "Хороший день"),
    (1, 5, 7.5, 8.0, "Отлично!"),
    (2, 3, 4.0, 6.0, "Устал"),
    (3, 2, 2.0, 5.0, "Плохо"),
    (4, 4, 5.5, 7.0, "Норм"),
    (5, 5, 8.0, 8.5, "Супер"),
    (6, 3, 3.0, 9.0, "Выходной"),
    (7, 4, 6.5, 7.0, "Хорошо"),
    (8, 2, 1.5, 4.5, "Болел"),
    (9, 3, 4.0, 8.0, "Ок"),
    (10, 5, 7.0, 7.5, "Энергично"),
    (11, 4, 5.0, 6.5, "Недосып"),
    (12, 3, 3.5, 7.0, "Средне"),
    (13, 4, 6.0, 8.0, "Хорошо"),
    (14, 5, 7.5, 8.0, "Лучший"),
]

for days_ago, mood, work, sleep, comment in test_data:
    date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    cur.execute("""
        INSERT INTO daily_records (user_id, record_date, mood, work_hours, sleep_hours, comment)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (MY_USER_ID, date, mood, work, sleep, comment))

conn.commit()
conn.close()

print(f"✅ Добавлено {len(test_data)} тестовых записей для пользователя {MY_USER_ID}")
print("Теперь запусти бота и нажми '📊 Статистика' → '📉 График'")