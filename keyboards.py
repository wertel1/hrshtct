

import telebot
from telebot.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главная постоянная клавиатура (ReplyKeyboard)."""
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        KeyboardButton("➕ Записать день"),
        KeyboardButton("📊 Статистика")
    )
    kb.add(
        KeyboardButton("📋 История"),
        KeyboardButton("⚙️ Настройки")
    )
    kb.add(
        KeyboardButton("❓ Помощь")
    )
    return kb


def get_mood_keyboard() -> InlineKeyboardMarkup:
    """Инлайн-клавиатура для оценки настроения (1–5)."""
    kb = InlineKeyboardMarkup(row_width=5)
    moods = [
        ("1 😞", "mood_1"),
        ("2 😐", "mood_2"),
        ("3 🙂", "mood_3"),
        ("4 😊", "mood_4"),
        ("5 🤩", "mood_5"),
    ]
    buttons = [InlineKeyboardButton(text, callback_data=data) for text, data in moods]
    kb.add(*buttons)
    return kb


def get_work_hours_keyboard() -> InlineKeyboardMarkup:
    """Инлайн-клавиатура для выбора часов работы/учёбы."""
    kb = InlineKeyboardMarkup(row_width=5)
    options = [
        ("0.5 ч", "work_0.5"),
        ("1 ч",   "work_1"),
        ("2 ч",   "work_2"),
        ("4 ч",   "work_4"),
        ("Другое", "work_custom"),
    ]
    buttons = [InlineKeyboardButton(text, callback_data=data) for text, data in options]
    kb.add(*buttons)
    return kb


def get_sleep_hours_keyboard() -> InlineKeyboardMarkup:
    """Инлайн-клавиатура для выбора часов сна."""
    kb = InlineKeyboardMarkup(row_width=5)
    options = [
        ("6 ч",    "sleep_6"),
        ("7 ч",    "sleep_7"),
        ("8 ч",    "sleep_8"),
        ("9 ч",    "sleep_9"),
        ("Другое", "sleep_custom"),
    ]
    buttons = [InlineKeyboardButton(text, callback_data=data) for text, data in options]
    kb.add(*buttons)
    return kb


def get_comment_keyboard() -> InlineKeyboardMarkup:
    """Инлайн-клавиатура с кнопкой «Пропустить» для комментария."""
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("⏭ Пропустить", callback_data="comment_skip"))
    return kb


def get_stats_keyboard() -> InlineKeyboardMarkup:
    """Инлайн-меню выбора периода/типа статистики."""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📅 За неделю",   callback_data="stats_week"),
        InlineKeyboardButton("🗓 За месяц",    callback_data="stats_month")
    )
    kb.add(
        InlineKeyboardButton("🔍 Мои инсайты", callback_data="stats_insights"),
        InlineKeyboardButton("📉 График",      callback_data="stats_chart")
    )
    return kb


def get_history_keyboard() -> InlineKeyboardMarkup:
    """Инлайн-меню для истории."""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📅 7 дней",  callback_data="history_7"),
        InlineKeyboardButton("🗓 30 дней", callback_data="history_30")
    )
    return kb


def get_confirm_clear_keyboard() -> InlineKeyboardMarkup:
    """Подтверждение очистки данных."""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✅ Да, удалить", callback_data="clear_confirm"),
        InlineKeyboardButton("❌ Отмена",       callback_data="clear_cancel")
    )
    return kb


def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Меню настроек."""
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("🔔 Изменить время напоминания", callback_data="settings_reminder"),
        InlineKeyboardButton("🗑 Очистить все данные",        callback_data="settings_clear"),
        InlineKeyboardButton("ℹ️ О боте",                     callback_data="settings_about")
    )
    return kb