import threading
import time
from datetime import datetime
import telebot
from config import BOT_TOKEN
from db_handler import *
from keyboards import *
from analyzer import *

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

@bot.message_handler(commands=['start'])
def start(m):
    user = m.from_user
    save_user(user.id, user.username or "", user.first_name or "")
    bot.send_message(m.chat.id, f"Привет, {user.first_name}! Я трекер настроения. Нажми /add или кнопку 'Записать'", reply_markup=main_kb())

@bot.message_handler(func=lambda m: m.text == "❓ Помощь")
def help(m):
    bot.send_message(m.chat.id, "Записывай настроение, работу и сон каждый день. Бот покажет статистику и графики.", reply_markup=main_kb())

@bot.message_handler(commands=['add'])
@bot.message_handler(func=lambda m: m.text == "➕ Записать")
def add(m):
    user_id = m.from_user.id
    save_user(user_id, m.from_user.username or "", m.from_user.first_name or "")
    if get_today(user_id):
        bot.send_message(m.chat.id, "Сегодня уже записано. Обновим!")
    user_data[user_id] = {"state": "mood"}
    bot.send_message(m.chat.id, "Шаг 1/4: Оцени настроение", reply_markup=mood_kb())

@bot.callback_query_handler(func=lambda c: c.data.startswith("mood_"))
def mood_cb(c):
    uid = c.from_user.id
    if user_data.get(uid, {}).get("state") != "mood":
        bot.answer_callback_query(c.id, "Начни с /add")
        return
    mood = int(c.data.split("_")[1])
    user_data[uid]["mood"] = mood
    user_data[uid]["state"] = "work"
    bot.edit_message_text(f"Настроение: {mood}/5 ✅", c.message.chat.id, c.message.message_id)
    bot.send_message(c.message.chat.id, "Шаг 2/4: Сколько работал?", reply_markup=work_kb())

@bot.callback_query_handler(func=lambda c: c.data.startswith("work_"))
def work_cb(c):
    uid = c.from_user.id
    if user_data.get(uid, {}).get("state") != "work":
        bot.answer_callback_query(c.id, "Начни сначала")
        return
    val = c.data.split("_")[1]
    if val == "custom":
        user_data[uid]["state"] = "work_custom"
        bot.edit_message_text("Введи часы (например: 3.5):", c.message.chat.id, c.message.message_id)
        return
    user_data[uid]["work"] = float(val)
    user_data[uid]["state"] = "sleep"
    bot.edit_message_text(f"Работа: {val}ч ✅", c.message.chat.id, c.message.message_id)
    bot.send_message(c.message.chat.id, "Шаг 3/4: Сколько спал?", reply_markup=sleep_kb())

@bot.callback_query_handler(func=lambda c: c.data.startswith("sleep_"))
def sleep_cb(c):
    uid = c.from_user.id
    if user_data.get(uid, {}).get("state") != "sleep":
        bot.answer_callback_query(c.id, "Начни сначала")
        return
    val = c.data.split("_")[1]
    if val == "custom":
        user_data[uid]["state"] = "sleep_custom"
        bot.edit_message_text("Введи часы сна (например: 7.5):", c.message.chat.id, c.message.message_id)
        return
    user_data[uid]["sleep"] = float(val)
    user_data[uid]["state"] = "comment"
    bot.edit_message_text(f"Сон: {val}ч ✅", c.message.chat.id, c.message.message_id)
    bot.send_message(c.message.chat.id, "Шаг 4/4: Комментарий или Пропустить", reply_markup=skip_kb())

@bot.callback_query_handler(func=lambda c: c.data == "skip")
def skip_cb(c):
    uid = c.from_user.id
    if user_data.get(uid, {}).get("state") != "comment":
        return
    save_final(c.message.chat.id, uid, None)

def save_final(chat_id, uid, comment):
    data = user_data.get(uid, {})
    save_record(uid, data.get("mood"), data.get("work"), data.get("sleep"), comment)
    emoji = EMOJI.get(data.get("mood"), "")
    text = f"✅ Сохранено!\nНастроение: {data.get('mood')}/5 {emoji}\nРабота: {data.get('work')}ч\nСон: {data.get('sleep')}ч"
    if comment:
        text += f"\n💬 {comment}"
    bot.send_message(chat_id, text, reply_markup=main_kb())
    user_data.pop(uid, None)

@bot.message_handler(func=lambda m: user_data.get(m.from_user.id, {}).get("state") in ["work_custom", "sleep_custom", "comment"])
def text_in(m):
    uid = m.from_user.id
    state = user_data.get(uid, {}).get("state")
    
    if state == "work_custom":
        try:
            h = float(m.text.replace(",", "."))
            if 0 <= h <= 24:
                user_data[uid]["work"] = h
                user_data[uid]["state"] = "sleep"
                bot.send_message(m.chat.id, f"Работа: {h}ч ✅")
                bot.send_message(m.chat.id, "Шаг 3/4: Сколько спал?", reply_markup=sleep_kb())
        except:
            bot.send_message(m.chat.id, "Введи число 0-24")
    
    elif state == "sleep_custom":
        try:
            h = float(m.text.replace(",", "."))
            if 0 <= h <= 24:
                user_data[uid]["sleep"] = h
                user_data[uid]["state"] = "comment"
                bot.send_message(m.chat.id, f"Сон: {h}ч ✅")
                bot.send_message(m.chat.id, "Шаг 4/4: Комментарий или напиши 'пропустить'")
        except:
            bot.send_message(m.chat.id, "Введи число 0-24")
    
    elif state == "comment":
        comment = None if m.text.lower() == "пропустить" else m.text
        save_final(m.chat.id, uid, comment)

@bot.message_handler(func=lambda m: m.text == "📊 Статистика")
def stats_menu(m):
    bot.send_message(m.chat.id, "Что хочешь?", reply_markup=stats_kb())

@bot.callback_query_handler(func=lambda c: c.data in ["stats_week", "stats_month"])
def stats_cb(c):
    days = 7 if c.data == "stats_week" else 30
    stats = get_stats(c.from_user.id, days)
    bot.edit_message_text(format_stats(stats, days), c.message.chat.id, c.message.message_id, reply_markup=stats_kb())

@bot.callback_query_handler(func=lambda c: c.data == "insights")
def insights_cb(c):
    uid = c.from_user.id
    records = get_records(uid, 30)
    if len(records) < 3:
        bot.edit_message_text("Нужно минимум 3 записи для инсайтов", c.message.chat.id, c.message.message_id, reply_markup=stats_kb())
        return
    sleep_avg = sum(r[3] for r in records)/len(records)
    work_avg = sum(r[2] for r in records)/len(records)
    mood_avg = sum(r[1] for r in records)/len(records)
    text = f"🔍 Инсайты (30 дней)\n\nСон: {sleep_avg:.1f}ч\nРабота: {work_avg:.1f}ч\nНастроение: {mood_avg:.1f}/5\n"
    if sleep_avg < 6:
        text += "⚠️ Спишь мало (<6ч)"
    elif sleep_avg >= 8:
        text += "✅ Хороший сон (8+ч)"
    if work_avg > 8:
        text += "\n⚠️ Много работаешь (>8ч)"
    bot.edit_message_text(text, c.message.chat.id, c.message.message_id, reply_markup=stats_kb())

@bot.callback_query_handler(func=lambda c: c.data == "chart")
def chart_cb(c):
    uid = c.from_user.id
    records = get_records(uid, 30)
    chart = make_chart(records)
    if chart:
        bot.send_photo(c.message.chat.id, chart, caption="📈 Динамика за 30 дней")
    else:
        bot.send_message(c.message.chat.id, "Нужно минимум 2 записи для графика!")

@bot.message_handler(func=lambda m: m.text == "📋 История")
def history_menu(m):
    bot.send_message(m.chat.id, "За какой период?", reply_markup=history_kb())

@bot.callback_query_handler(func=lambda c: c.data.startswith("hist_"))
def history_cb(c):
    days = int(c.data.split("_")[1])
    records = get_records(c.from_user.id, days)
    bot.edit_message_text(format_history(records, days), c.message.chat.id, c.message.message_id, reply_markup=history_kb())

@bot.message_handler(func=lambda m: m.text == "⚙️ Настройки")
def settings_menu(m):
    bot.send_message(m.chat.id, "Настройки", reply_markup=settings_kb())

@bot.callback_query_handler(func=lambda c: c.data == "set_remind")
def remind_cb(c):
    uid = c.from_user.id
    user_data[uid] = {"state": "remind"}
    bot.edit_message_text("Введи час (0-23):", c.message.chat.id, c.message.message_id)

@bot.callback_query_handler(func=lambda c: c.data == "set_clear")
def clear_cb(c):
    bot.edit_message_text("Удалить все данные?", c.message.chat.id, c.message.message_id, reply_markup=confirm_kb())

@bot.callback_query_handler(func=lambda c: c.data == "clear_yes")
def clear_yes(c):
    clear_data(c.from_user.id)
    bot.edit_message_text("✅ Данные удалены", c.message.chat.id, c.message.message_id)

@bot.callback_query_handler(func=lambda c: c.data == "clear_no")
def clear_no(c):
    bot.edit_message_text("Отмена", c.message.chat.id, c.message.message_id)

@bot.message_handler(func=lambda m: user_data.get(m.from_user.id, {}).get("state") == "remind")
def remind_text(m):
    uid = m.from_user.id
    try:
        h = int(m.text)
        if 0 <= h <= 23:
            update_remind(uid, h)
            bot.send_message(m.chat.id, f"✅ Напоминание в {h}:00", reply_markup=main_kb())
        else:
            raise ValueError
    except:
        bot.send_message(m.chat.id, "Введи число 0-23")
    user_data.pop(uid, None)

@bot.message_handler(commands=['clear'])
def clear_cmd(m):
    bot.send_message(m.chat.id, "Удалить данные?", reply_markup=confirm_kb())

def reminder():
    while True:
        now = datetime.now()
        for u in get_all_users():
            if u[1] == now.hour and not get_today(u[0]):
                bot.send_message(u[0], "🔔 Напоминание! Запиши сегодняшний день.", reply_markup=main_kb())
        time.sleep(3600)

if __name__ == "__main__":
    init_db()
    threading.Thread(target=reminder, daemon=True).start()
    print("✅ Бот запущен")
    bot.infinity_polling()