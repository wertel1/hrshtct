import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from io import BytesIO
import sqlite3

load_dotenv()
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

conn = sqlite3.connect('mood_tracker.db', check_same_thread=False)
cur = conn.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        mood INTEGER,
        work REAL,
        sleep REAL,
        comment TEXT
    )
''')
conn.commit()

data = {}

def main_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add('Добавить день', 'Статистика')
    kb.add('История', 'Настройки')
    return kb

def mood_kb():
    kb = InlineKeyboardMarkup(row_width=5)
    for i, e in [(1,'😞'),(2,'😐'),(3,'🙂'),(4,'😊'),(5,'🤩')]:
        kb.add(InlineKeyboardButton(f"{i}{e}", callback_data=f"m_{i}"))
    return kb

def stats_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("Неделя", callback_data="s_week"),
        InlineKeyboardButton("Месяц", callback_data="s_month"),
        InlineKeyboardButton("Инсайты", callback_data="s_insights"),
        InlineKeyboardButton("График", callback_data="s_chart")
    )
    return kb

def skip_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add('Пропустить')
    return kb

def save(user_id, mood, work, sleep, comment):
    cur.execute("INSERT INTO entries (user_id, date, mood, work, sleep, comment) VALUES (?,?,?,?,?,?)",
                (user_id, datetime.now().strftime('%Y-%m-%d'), mood, work, sleep, comment))
    conn.commit()

def get(user_id, limit=30):
    cur.execute("SELECT date, mood, work, sleep, comment FROM entries WHERE user_id = ? ORDER BY date DESC LIMIT ?", (user_id, limit))
    return cur.fetchall()

def get_all(user_id):
    cur.execute("SELECT date, mood, work, sleep FROM entries WHERE user_id = ? ORDER BY date", (user_id,))
    return cur.fetchall()

def clear(user_id):
    cur.execute("DELETE FROM entries WHERE user_id = ?", (user_id,))
    conn.commit()

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "Трекер настроения.\n/add - записать день", reply_markup=main_kb())


@bot.message_handler(commands=['add'])
@bot.message_handler(func=lambda m: m.text == 'Добавить день')
def add(m):
    data[m.chat.id] = {'step': 'mood'}
    bot.send_message(m.chat.id, "Настроение:", reply_markup=mood_kb())

@bot.callback_query_handler(func=lambda c: c.data.startswith('m_'))
def mood(c):
    mood = int(c.data.split('_')[1])
    uid = c.message.chat.id
    data[uid] = {'step': 'work', 'mood': mood}
    bot.edit_message_text(f"Настроение: {mood}/5 ", uid, c.message.message_id)
    bot.answer_callback_query(c.id)
    bot.send_message(uid, "Работа (часы):", reply_markup=main_kb())

@bot.message_handler(func=lambda m: data.get(m.chat.id, {}).get('step') == 'work')
def work(m):
    try:
        data[m.chat.id]['work'] = float(m.text.replace(',', '.'))
        data[m.chat.id]['step'] = 'sleep'
        bot.send_message(m.chat.id, "Сон (часы):", reply_markup=main_kb())
    except:
        bot.send_message(m.chat.id, "Введи число")

@bot.message_handler(func=lambda m: data.get(m.chat.id, {}).get('step') == 'sleep')
def sleep(m):
    try:
        data[m.chat.id]['sleep'] = float(m.text.replace(',', '.'))
        data[m.chat.id]['step'] = 'comment'
        bot.send_message(m.chat.id, "Комментарий", reply_markup=skip_kb())
    except:
        bot.send_message(m.chat.id, "Введи число")

@bot.message_handler(func=lambda m: data.get(m.chat.id, {}).get('step') == 'comment')
def comment(m):
    uid = m.chat.id
    d = data[uid]
    
    if m.text == 'Пропустить':
        comment = ''
    else:
        comment = m.text
    
    save(uid, d['mood'], d['work'], d['sleep'], comment)
    del data[uid]
    
    bot.send_message(uid, f" Сохранено!\nНастроение: {d['mood']}/5\nРабота: {d['work']}ч\nСон: {d['sleep']}ч\nКоммент: {comment if comment else 'нет'}", reply_markup=main_kb())

@bot.message_handler(func=lambda m: m.text == 'Статистика')
def stats(m):
    bot.send_message(m.chat.id, "Что хочешь?", reply_markup=stats_kb())

@bot.callback_query_handler(func=lambda c: c.data.startswith('s_'))
def stats_cb(c):
    uid = c.message.chat.id
    action = c.data.split('_')[1]
    
    if action == 'insights':
        rows = get_all(uid)
        if len(rows) < 3:
            text = "Нужно минимум 3 дня"
        else:
            avg_mood = sum(r[1] for r in rows) / len(rows)
            avg_work = sum(r[2] for r in rows) / len(rows)
            avg_sleep = sum(r[3] for r in rows) / len(rows)
            best = max(rows, key=lambda x: x[1])
            text = f"🔍 Инсайты\n\nНастроение: {avg_mood:.1f}/5\nРабота: {avg_work:.1f}ч\nСон: {avg_sleep:.1f}ч\n\n🏆 Лучший день: {best[0]} | настроение {best[1]}/5"
        bot.edit_message_text(text, uid, c.message.message_id)
        bot.answer_callback_query(c.id)
        return
    
    if action == 'chart':
        rows = get_all(uid)
        if not rows:
            bot.edit_message_text("Нет данных", uid, c.message.message_id)
            bot.answer_callback_query(c.id)
            return
        dates = [r[0] for r in rows]
        moods = [r[1] for r in rows]
        works = [r[2] for r in rows]
        sleeps = [r[3] for r in rows]
        plt.figure(figsize=(10, 5))
        plt.plot(dates, moods, 'o-', label='Настроение', linewidth=2)
        plt.plot(dates, sleeps, 's-', label='Сон', linewidth=2)
        plt.plot(dates, works, '^-', label='Работа', linewidth=2)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        bot.send_photo(uid, buf)
        bot.delete_message(uid, c.message.message_id)
        bot.answer_callback_query(c.id)
        return
    
    days = 7 if action == 'week' else 30
    period = 'неделю' if action == 'week' else 'месяц'
    rows = get(uid, days)
    if not rows:
        text = f"Нет данных за {period}"
    else:
        avg_mood = sum(r[1] for r in rows) / len(rows)
        avg_work = sum(r[2] for r in rows) / len(rows)
        avg_sleep = sum(r[3] for r in rows) / len(rows)
        text = f"📊 За {period}\n\nДней: {len(rows)}\nНастроение: {avg_mood:.1f}/5\nРабота: {avg_work:.1f}ч\nСон: {avg_sleep:.1f}ч"
    bot.edit_message_text(text, uid, c.message.message_id)
    bot.answer_callback_query(c.id)

@bot.message_handler(func=lambda m: m.text == 'История')
def history(m):
    rows = get(m.chat.id, 20)
    if not rows:
        text = "Нет записей"
    else:
        text = "📋 История\n\n"
        for r in rows:
            text += f"{r[0]} | Настроение: {r[1]} | Работа: {r[2]}ч | Сон: {r[3]}ч\n"
            if r[4]:
                text += f"💬 {r[4]}\n"
            text += "---\n"
    bot.send_message(m.chat.id, text, reply_markup=main_kb())

@bot.message_handler(func=lambda m: m.text == 'Настройки')
def settings(m):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Очистить данные", callback_data="clear"))
    bot.send_message(m.chat.id, "Настройки", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data == 'clear')
def clear_cb(c):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(" Да", callback_data="clear_yes"), InlineKeyboardButton(" Нет", callback_data="clear_no"))
    bot.edit_message_text("Удалить все данные?", c.message.chat.id, c.message.message_id, reply_markup=kb)
    bot.answer_callback_query(c.id)

@bot.callback_query_handler(func=lambda c: c.data.startswith('clear_'))
def clear_yes(c):
    if c.data == 'clear_yes':
        clear(c.message.chat.id)
        text = "Данные удалены"
    else:
        text = " Отмена"
    bot.edit_message_text(text, c.message.chat.id, c.message.message_id)
    bot.answer_callback_query(c.id)

print("Бот запущен")
bot.infinity_polling()