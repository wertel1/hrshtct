import threading
import time
from datetime import datetime
import telebot

from config import BOT_TOKEN
from db_handler import init_db, save_user, get_user, update_remind_hour, save_record, record_exists_today, get_records, get_stats, clear_user_data, get_sleep_correlation, get_work_correlation, get_all_users, get_best_worst_days, get_weekday_stats, get_history
from keyboards import get_main_keyboard, get_mood_keyboard, get_work_keyboard, get_sleep_keyboard, get_skip_keyboard, get_stats_keyboard, get_history_keyboard, get_settings_keyboard, get_confirm_keyboard
from analyzer import format_stats, format_insights, format_history, generate_chart

bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    save_user(user.id, user.username or "", user.first_name or "")
    
    text = f"""👋 Привет, {user.first_name or 'друг'}!

Я бот для отслеживания настроения, сна и продуктивности.

📌 Что я умею:
• Записывать твоё состояние каждый день
• Показывать статистику
• Находить связи между сном, работой и настроением

🚀 Нажми «➕ Записать день» и ответь на 4 вопроса!"""
    
    bot.send_message(message.chat.id, text, reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda m: m.text == "❓ Помощь")
def help_msg(message):
    text = """📖 Справка

➕ Записать день - начать опрос
📊 Статистика - посмотреть аналитику
📋 История - прошлые записи
⚙️ Настройки - изменить напоминания

Как заполнять:
1. Оцени настроение (1-5)
2. Сколько работал/учился
3. Сколько спал
4. Комментарий (по желанию)

Заполняй каждый день для точной аналитики!"""
    
    bot.send_message(message.chat.id, text, reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda m: m.text == "➕ Записать день")
def add_day(message):
    user_id = message.from_user.id
    save_user(user_id, message.from_user.username or "", message.from_user.first_name or "")
    
    if record_exists_today(user_id):
        bot.send_message(message.chat.id, "За сегодня уже есть запись. Обновим её!")
    
    user_data[user_id] = {"state": "mood"}
    bot.send_message(message.chat.id, "Шаг 1/4\n\nОцени настроение сегодня:", reply_markup=get_mood_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith("mood_"))
def mood_handler(call):
    user_id = call.from_user.id
    if user_data.get(user_id, {}).get("state") != "mood":
        bot.answer_callback_query(call.id, "Начни с /add")
        return
    
    mood = int(call.data.split("_")[1])
    user_data[user_id]["mood"] = mood
    user_data[user_id]["state"] = "work"
    
    bot.edit_message_text(f"Настроение: {mood}/5 ✅", call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Шаг 2/4\n\nСколько часов работал/учился?", reply_markup=get_work_keyboard())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("work_"))
def work_handler(call):
    user_id = call.from_user.id
    if user_data.get(user_id, {}).get("state") != "work":
        bot.answer_callback_query(call.id, "Начни сначала")
        return
    
    val = call.data.split("_")[1]
    
    if val == "custom":
        user_data[user_id]["state"] = "work_custom"
        bot.edit_message_text("Введи количество часов (например: 3.5 или 6):", call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    hours = float(val)
    user_data[user_id]["work_hours"] = hours
    user_data[user_id]["state"] = "sleep"
    
    bot.edit_message_text(f"Работа: {hours}ч ✅", call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Шаг 3/4\n\nСколько часов спал?", reply_markup=get_sleep_keyboard())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("sleep_"))
def sleep_handler(call):
    user_id = call.from_user.id
    if user_data.get(user_id, {}).get("state") != "sleep":
        bot.answer_callback_query(call.id, "Начни сначала")
        return
    
    val = call.data.split("_")[1]
    
    if val == "custom":
        user_data[user_id]["state"] = "sleep_custom"
        bot.edit_message_text("Введи количество часов сна (например: 7.5):", call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    hours = float(val)
    user_data[user_id]["sleep_hours"] = hours
    user_data[user_id]["state"] = "comment"
    
    bot.edit_message_text(f"Сон: {hours}ч ✅", call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Шаг 4/4\n\nДобавь комментарий или нажми «Пропустить»:", reply_markup=get_skip_keyboard())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "skip")
def skip_handler(call):
    user_id = call.from_user.id
    if user_data.get(user_id, {}).get("state") != "comment":
        bot.answer_callback_query(call.id)
        return
    
    save_final(call.message.chat.id, user_id, None)
    bot.answer_callback_query(call.id)

def save_final(chat_id, user_id, comment):
    data = user_data.get(user_id, {})
    
    save_record(
        user_id=user_id,
        mood=data.get("mood"),
        work_hours=data.get("work_hours"),
        sleep_hours=data.get("sleep_hours"),
        comment=comment
    )
    
    mood_emoji = {1: "😞", 2: "😐", 3: "🙂", 4: "😊", 5: "🤩"}
    
    text = f"✅ Сохранено!\n\n"
    text += f"😊 Настроение: {data.get('mood')}/5 {mood_emoji.get(data.get('mood'), '')}\n"
    text += f"💼 Работа: {data.get('work_hours')}ч\n"
    text += f"😴 Сон: {data.get('sleep_hours')}ч"
    if comment:
        text += f"\n💬 {comment}"
    text += "\n\nОтлично! Продолжай в том же духе 💪"
    
    bot.send_message(chat_id, text, reply_markup=get_main_keyboard())
    user_data.pop(user_id, None)

@bot.message_handler(func=lambda m: user_data.get(m.from_user.id, {}).get("state") in ["work_custom", "sleep_custom", "comment"])
def text_handler(message):
    user_id = message.from_user.id
    state = user_data.get(user_id, {}).get("state")
    
    if state == "work_custom":
        try:
            hours = float(message.text.replace(",", "."))
            if 0 <= hours <= 24:
                user_data[user_id]["work_hours"] = hours
                user_data[user_id]["state"] = "sleep"
                bot.send_message(message.chat.id, f"Работа: {hours}ч ✅")
                bot.send_message(message.chat.id, "Шаг 3/4\n\nСколько часов спал?", reply_markup=get_sleep_keyboard())
            else:
                raise ValueError
        except:
            bot.send_message(message.chat.id, "Введи число от 0 до 24 (например: 6.5)")
    
    elif state == "sleep_custom":
        try:
            hours = float(message.text.replace(",", "."))
            if 0 <= hours <= 24:
                user_data[user_id]["sleep_hours"] = hours
                user_data[user_id]["state"] = "comment"
                bot.send_message(message.chat.id, f"Сон: {hours}ч ✅")
                bot.send_message(message.chat.id, "Шаг 4/4\n\nДобавь комментарий или напиши «пропустить»:")
            else:
                raise ValueError
        except:
            bot.send_message(message.chat.id, "Введи число от 0 до 24 (например: 7.5)")
    
    elif state == "comment":
        comment = None if message.text.lower() == "пропустить" else message.text
        save_final(message.chat.id, user_id, comment)

@bot.message_handler(func=lambda m: m.text == "📊 Статистика")
def stats_menu(message):
    bot.send_message(message.chat.id, "Что хочешь узнать?", reply_markup=get_stats_keyboard())

@bot.callback_query_handler(func=lambda call: call.data in ["stats_week", "stats_month"])
def stats_handler(call):
    user_id = call.from_user.id
    days = 7 if call.data == "stats_week" else 30
    stats = get_stats(user_id, days)
    text = format_stats(stats, days)
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=get_stats_keyboard())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "stats_insights")
def insights_handler(call):
    user_id = call.from_user.id
    
    sleep_data = get_sleep_correlation(user_id)
    work_data = get_work_correlation(user_id)
    best, worst = get_best_worst_days(user_id)
    weekday_data = get_weekday_stats(user_id)
    
    text = format_insights(sleep_data, work_data, best, worst, weekday_data)
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=get_stats_keyboard())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "stats_chart")
def chart_handler(call):
    user_id = call.from_user.id
    bot.answer_callback_query(call.id, "Генерирую график...")
    
    records = get_records(user_id, 30)
    chart = generate_chart(records)
    
    if chart:
        bot.send_photo(call.message.chat.id, chart, caption="📈 Динамика за последние 30 дней")
    else:
        bot.send_message(call.message.chat.id, "📭 Недостаточно данных для графика. Нужно минимум 2 записи!")

@bot.message_handler(func=lambda m: m.text == "📋 История")
def history_menu(message):
    bot.send_message(message.chat.id, "За какой период?", reply_markup=get_history_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith("hist_"))
def history_handler(call):
    user_id = call.from_user.id
    days = int(call.data.split("_")[1])
    records = get_history(user_id, days)
    text = format_history(records, days)
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=get_history_keyboard())
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.text == "⚙️ Настройки")
def settings_menu(message):
    user = get_user(message.from_user.id)
    hour = user[4] if user else 21
    text = f"⚙️ Настройки\n\n🔔 Напоминания: {hour}:00\n\nЧто хочешь изменить?"
    bot.send_message(message.chat.id, text, reply_markup=get_settings_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "set_reminder")
def set_reminder(call):
    user_id = call.from_user.id
    user_data[user_id] = {"state": "reminder"}
    bot.edit_message_text("Введи час для напоминания (0-23):\nНапример: 9 или 21", 
                          call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: user_data.get(m.from_user.id, {}).get("state") == "reminder")
def reminder_hour_handler(message):
    user_id = message.from_user.id
    try:
        hour = int(message.text)
        if 0 <= hour <= 23:
            update_remind_hour(user_id, hour)
            bot.send_message(message.chat.id, f"✅ Напоминания установлены на {hour}:00", reply_markup=get_main_keyboard())
        else:
            raise ValueError
    except:
        bot.send_message(message.chat.id, "Введи число от 0 до 23")
    user_data.pop(user_id, None)

@bot.callback_query_handler(func=lambda call: call.data == "set_clear")
def clear_confirm(call):
    bot.edit_message_text("🗑 Ты уверен? Все данные будут удалены!", 
                          call.message.chat.id, call.message.message_id, reply_markup=get_confirm_keyboard())
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "clear_yes")
def clear_data(call):
    user_id = call.from_user.id
    clear_user_data(user_id)
    bot.edit_message_text("✅ Все данные удалены", call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "clear_no")
def clear_cancel(call):
    bot.edit_message_text("Отмена", call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)

@bot.message_handler(commands=['clear'])
def clear_command(message):
    bot.send_message(message.chat.id, "🗑 Удалить все данные?", reply_markup=get_confirm_keyboard())

def reminder_worker():
    while True:
        try:
            now = datetime.now()
            users = get_all_users()
            for user in users:
                if user[1] == now.hour and not record_exists_today(user[0]):
                    bot.send_message(user[0], "🔔 Напоминание!\n\nТы ещё не записал сегодняшний день. Нажми /add", reply_markup=get_main_keyboard())
        except Exception as e:
            print(f"Ошибка: {e}")
        time.sleep(3600)

if __name__ == "__main__":
    init_db()
    
    t = threading.Thread(target=reminder_worker, daemon=True)
    t.start()
    
    print("✅ Бот запущен!")
    bot.infinity_polling()