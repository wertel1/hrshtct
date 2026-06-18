from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("➕ Записать"), KeyboardButton("📊 Статистика"))
    kb.add(KeyboardButton("📋 История"), KeyboardButton("⚙️ Настройки"))
    kb.add(KeyboardButton("❓ Помощь"))
    return kb

def mood_kb():
    kb = InlineKeyboardMarkup(row_width=5)
    for i, e in [(1,"😞"),(2,"😐"),(3,"🙂"),(4,"😊"),(5,"🤩")]:
        kb.add(InlineKeyboardButton(f"{i}{e}", callback_data=f"mood_{i}"))
    return kb

def work_kb():
    kb = InlineKeyboardMarkup(row_width=3)
    for h in ["0.5","1","2","4","6","8"]:
        kb.add(InlineKeyboardButton(f"{h}ч", callback_data=f"work_{h}"))
    kb.add(InlineKeyboardButton("Другое", callback_data="work_custom"))
    return kb

def sleep_kb():
    kb = InlineKeyboardMarkup(row_width=3)
    for h in ["4","6","7","8","9"]:
        kb.add(InlineKeyboardButton(f"{h}ч", callback_data=f"sleep_{h}"))
    kb.add(InlineKeyboardButton("Другое", callback_data="sleep_custom"))
    return kb

def skip_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("⏭ Пропустить", callback_data="skip"))
    return kb

def stats_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("📅 Неделя", callback_data="stats_week"))
    kb.add(InlineKeyboardButton("🗓 Месяц", callback_data="stats_month"))
    kb.add(InlineKeyboardButton("🔍 Инсайты", callback_data="insights"))
    kb.add(InlineKeyboardButton("📉 График", callback_data="chart"))
    return kb

def history_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("7 дней", callback_data="hist_7"))
    kb.add(InlineKeyboardButton("30 дней", callback_data="hist_30"))
    return kb

def settings_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔔 Напоминание", callback_data="set_remind"))
    kb.add(InlineKeyboardButton("🗑 Очистить", callback_data="set_clear"))
    return kb

def confirm_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Да", callback_data="clear_yes"))
    kb.add(InlineKeyboardButton("❌ Нет", callback_data="clear_no"))
    return kb