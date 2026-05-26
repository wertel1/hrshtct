

BOT_TOKEN = "..."


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "mood_tracker",
    "user": "postgres",
    "password": "свой пароль" 
}


class States:
    IDLE = "idle"
    WAITING_MOOD = "waiting_mood"
    WAITING_WORK = "waiting_work"
    WAITING_WORK_CUSTOM = "waiting_work_custom"
    WAITING_SLEEP = "waiting_sleep"
    WAITING_SLEEP_CUSTOM = "waiting_sleep_custom"
    WAITING_COMMENT = "waiting_comment"
    WAITING_CLEAR_CONFIRM = "waiting_clear_confirm"
    WAITING_SETTINGS_HOUR = "waiting_settings_hour"