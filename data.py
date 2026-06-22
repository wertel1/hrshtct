
import sqlite3
from datetime import datetime, timedelta

USER_ID = 11111

conn = sqlite3.connect('mood_tracker.db')
cur = conn.cursor()

cur.execute("DELETE FROM entries WHERE user_id = ?", (USER_ID,))

data = [
    (0, 5, 6.0, 8.0, "Отлично выспался, продуктивный день"),
    (1, 4, 7.5, 7.0, "Хороший день, но немного устал"),
    (2, 3, 4.0, 6.5, "Средний день, не хватило энергии"),
    (3, 2, 2.0, 5.0, "Плохо спал, ничего не успел"),
    (4, 4, 5.5, 7.5, "Норм, всё успел по плану"),
    (5, 5, 8.0, 8.5, "Супер день! Выполнил всё"),
    (6, 3, 3.0, 9.0, "Выходной, отдыхал весь день"),
    (7, 4, 6.5, 7.0, "Хорошо, но могло быть лучше"),
    (8, 2, 1.5, 4.5, "Заболел, плохо себя чувствовал"),
    (9, 3, 4.0, 8.0, "Постепенно прихожу в норму"),
    (10, 5, 7.0, 7.5, "Энергичный день, много успел"),
    (11, 4, 5.0, 6.0, "Недосып, но настроение норм"),
    (12, 3, 3.5, 7.0, "Средненький день"),
    (13, 4, 6.0, 8.0, "Хороший день, выспался отлично"),
    (14, 5, 7.5, 8.0, "Лучший день за неделю!"),
]

for days, mood, work, sleep, comment in data:
    date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    cur.execute("INSERT INTO entries (user_id, date, mood, work, sleep, comment) VALUES (?,?,?,?,?,?)",
                (USER_ID, date, mood, work, sleep, comment))

conn.commit()
conn.close()
