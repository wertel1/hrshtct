#  Mood & Productivity Tracker Bot

Telegram-бот для отслеживания ежедневного настроения, сна и продуктивности
с аналитикой на основе реальных данных.

##  Возможности

-  Ежедневный ввод данных: настроение, сон, работа, комментарий
-  Статистика за 7 и 30 дней
-  Персональные инсайты и корреляции
-  Графики динамики показателей
-  Напоминания в заданное время

## 🛠 Установка

### 1. Клонировать репозиторий
```bash
git clone https://github.com/your-username/mood-tracker-bot.git
cd mood-tracker-bot
```

## Создание виртуального окружения 
```bash
- python -m venv venv
- # Windows:
- venv\Scripts\activate
```

## Установка зависимостей
- pip install -r requirements.txt

## Подготовка базы данных
- CREATE DATABASE mood_tracker;

## Настройка конфигурации
```bash
BOT_TOKEN = "ВАШ_ТОКЕН_ОТ_@BotFather"

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "mood_tracker",
    "user": "postgres",
    "password": "ВАШ_ПАРОЛЬ_ОТ_POSTGRESQL"
}
```
## Запуск бота
- python bot.py