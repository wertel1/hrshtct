from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("➕ Записать день"))
    kb.add(KeyboardButton("📊 Статистика"))
    kb.add(KeyboardButton("📋 История"))
    kb.add(KeyboardButton("⚙️ Настройки"))
    kb.add(KeyboardButton("❓ Помощь"))
    return kb

def get_mood_keyboard():
    kb = InlineKeyboardMarkup(row_width=5)
    moods = [("1 😞", "1"), ("2 😐", "2"), ("3 🙂", "3"), ("4 😊", "4"), ("5 🤩", "5")]
    for text, val in moods:
        kb.add(InlineKeyboardButton(text, callback_data=f"mood_{val}"))
    return kb

def get_work_keyboard():
    kb = InlineKeyboardMarkup(row_width=3)
    for val in ["0.5", "1", "2", "4", "6", "8"]:
        kb.add(InlineKeyboardButton(f"{val} ч", callback_data=f"work_{val}"))
    kb.add(InlineKeyboardButton("Другое", callback_data="work_custom"))
    return kb

def get_sleep_keyboard():
    kb = InlineKeyboardMarkup(row_width=3)
    for val in ["4", "6", "7", "8", "9"]:
        kb.add(InlineKeyboardButton(f"{val} ч", callback_data=f"sleep_{val}"))
    kb.add(InlineKeyboardButton("Другое", callback_data="sleep_custom"))
    return kb

def get_skip_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("⏭ Пропустить", callback_data="skip"))
    return kb

def get_stats_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("📅 За неделю", callback_data="stats_week"))
    kb.add(InlineKeyboardButton("🗓 За месяц", callback_data="stats_month"))
    kb.add(InlineKeyboardButton("🔍 Инсайты", callback_data="stats_insights"))
    kb.add(InlineKeyboardButton("📉 График", callback_data="stats_chart"))  # Добавь эту строку
    return kb

def get_history_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("7 дней", callback_data="hist_7"))
    kb.add(InlineKeyboardButton("30 дней", callback_data="hist_30"))
    return kb

def get_settings_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔔 Время напоминания", callback_data="set_reminder"))
    kb.add(InlineKeyboardButton("🗑 Очистить данные", callback_data="set_clear"))
    return kb

def get_confirm_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Да", callback_data="clear_yes"))
    kb.add(InlineKeyboardButton("❌ Нет", callback_data="clear_no"))
    return kb