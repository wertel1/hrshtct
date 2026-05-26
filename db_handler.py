

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date
from config import DB_CONFIG
import logging

logger = logging.getLogger(__name__)


def get_connection():
    """Устанавливает соединение с PostgreSQL."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        logger.error(f"Ошибка подключения к БД: {e}")
        raise


def init_db():
    """Инициализация базы данных: создание таблиц если не существуют."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:

            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id     BIGINT PRIMARY KEY,
                    username    VARCHAR(255),
                    first_name  VARCHAR(255),
                    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    remind_hour INTEGER DEFAULT 21
                );
            """)


            cur.execute("""
                CREATE TABLE IF NOT EXISTS daily_records (
                    id           SERIAL PRIMARY KEY,
                    user_id      BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    record_date  DATE NOT NULL DEFAULT CURRENT_DATE,
                    mood         INTEGER NOT NULL CHECK (mood BETWEEN 1 AND 5),
                    work_hours   NUMERIC(4,1) NOT NULL CHECK (work_hours >= 0),
                    sleep_hours  NUMERIC(4,1) NOT NULL CHECK (sleep_hours >= 0),
                    comment      TEXT,
                    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, record_date)
                );
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_records_user_date
                ON daily_records(user_id, record_date DESC);
            """)

        conn.commit()
        logger.info("База данных инициализирована успешно.")
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Ошибка инициализации БД: {e}")
        raise
    finally:
        conn.close()



def upsert_user(user_id: int, username: str, first_name: str):
    """Создаёт или обновляет пользователя."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (user_id, username, first_name)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE
                    SET username   = EXCLUDED.username,
                        first_name = EXCLUDED.first_name;
            """, (user_id, username, first_name))
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"upsert_user error: {e}")
    finally:
        conn.close()


def get_user(user_id: int) -> dict | None:
    """Возвращает данные пользователя или None."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE user_id = %s;", (user_id,))
            return cur.fetchone()
    finally:
        conn.close()


def update_remind_hour(user_id: int, hour: int):
    """Обновляет час напоминания для пользователя."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET remind_hour = %s WHERE user_id = %s;",
                (hour, user_id)
            )
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"update_remind_hour error: {e}")
    finally:
        conn.close()



def add_record(user_id: int, mood: int, work_hours: float,
               sleep_hours: float, comment: str | None = None) -> bool:
    """
    Добавляет или обновляет запись за сегодня.
    Возвращает True при успехе.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO daily_records
                    (user_id, record_date, mood, work_hours, sleep_hours, comment)
                VALUES (%s, CURRENT_DATE, %s, %s, %s, %s)
                ON CONFLICT (user_id, record_date) DO UPDATE
                    SET mood        = EXCLUDED.mood,
                        work_hours  = EXCLUDED.work_hours,
                        sleep_hours = EXCLUDED.sleep_hours,
                        comment     = EXCLUDED.comment,
                        created_at  = CURRENT_TIMESTAMP;
            """, (user_id, mood, work_hours, sleep_hours, comment))
        conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"add_record error: {e}")
        return False
    finally:
        conn.close()


def get_records(user_id: int, days: int = 7) -> list[dict]:
    """Возвращает записи пользователя за последние N дней."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT *
                FROM daily_records
                WHERE user_id = %s
                  AND record_date >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY record_date DESC;
            """, (user_id, days))
            return cur.fetchall()
    finally:
        conn.close()


def record_exists_today(user_id: int) -> bool:
    """Проверяет, есть ли уже запись за сегодня."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 1 FROM daily_records
                WHERE user_id = %s AND record_date = CURRENT_DATE;
            """, (user_id,))
            return cur.fetchone() is not None
    finally:
        conn.close()


def clear_user_data(user_id: int) -> bool:
    """Удаляет все записи пользователя."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM daily_records WHERE user_id = %s;",
                (user_id,)
            )
        conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"clear_user_data error: {e}")
        return False
    finally:
        conn.close()


def get_stats(user_id: int, days: int = 7) -> dict | None:
    """
    Возвращает агрегированную статистику за период:
    средние значения, максимумы, минимумы и количество записей.
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    COUNT(*)                        AS total_records,
                    ROUND(AVG(mood), 2)             AS avg_mood,
                    MAX(mood)                       AS max_mood,
                    MIN(mood)                       AS min_mood,
                    ROUND(AVG(work_hours), 2)       AS avg_work,
                    MAX(work_hours)                 AS max_work,
                    ROUND(AVG(sleep_hours), 2)      AS avg_sleep,
                    MAX(sleep_hours)                AS max_sleep,
                    MIN(sleep_hours)                AS min_sleep
                FROM daily_records
                WHERE user_id = %s
                  AND record_date >= CURRENT_DATE - INTERVAL '%s days';
            """, (user_id, days))
            return cur.fetchone()
    finally:
        conn.close()


def get_best_worst_days(user_id: int, days: int = 30) -> dict:
    """Возвращает лучший и худший день по настроению за период."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
           
            cur.execute("""
                SELECT record_date, mood, work_hours, sleep_hours
                FROM daily_records
                WHERE user_id = %s
                  AND record_date >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY mood DESC, sleep_hours DESC
                LIMIT 1;
            """, (user_id, days))
            best = cur.fetchone()

         
            cur.execute("""
                SELECT record_date, mood, work_hours, sleep_hours
                FROM daily_records
                WHERE user_id = %s
                  AND record_date >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY mood ASC, sleep_hours ASC
                LIMIT 1;
            """, (user_id, days))
            worst = cur.fetchone()

        return {"best": best, "worst": worst}
    finally:
        conn.close()


def get_sleep_mood_correlation(user_id: int, days: int = 30) -> list[dict]:
    """
    Анализирует связь между сном и настроением:
    группирует записи по диапазонам сна.
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    CASE
                        WHEN sleep_hours < 6  THEN '< 6 ч'
                        WHEN sleep_hours < 7  THEN '6–7 ч'
                        WHEN sleep_hours < 8  THEN '7–8 ч'
                        WHEN sleep_hours < 9  THEN '8–9 ч'
                        ELSE '≥ 9 ч'
                    END AS sleep_range,
                    ROUND(AVG(mood), 2)       AS avg_mood,
                    ROUND(AVG(work_hours), 2) AS avg_work,
                    COUNT(*)                  AS records
                FROM daily_records
                WHERE user_id = %s
                  AND record_date >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY sleep_range
                ORDER BY MIN(sleep_hours);
            """, (user_id, days))
            return cur.fetchall()
    finally:
        conn.close()


def get_work_mood_correlation(user_id: int, days: int = 30) -> list[dict]:
    """
    Анализирует связь между рабочими часами и настроением.
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    CASE
                        WHEN work_hours < 2  THEN '< 2 ч'
                        WHEN work_hours < 4  THEN '2–4 ч'
                        WHEN work_hours < 6  THEN '4–6 ч'
                        WHEN work_hours < 8  THEN '6–8 ч'
                        ELSE '≥ 8 ч'
                    END AS work_range,
                    ROUND(AVG(mood), 2)        AS avg_mood,
                    ROUND(AVG(sleep_hours), 2) AS avg_sleep,
                    COUNT(*)                   AS records
                FROM daily_records
                WHERE user_id = %s
                  AND record_date >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY work_range
                ORDER BY MIN(work_hours);
            """, (user_id, days))
            return cur.fetchall()
    finally:
        conn.close()


def get_weekday_stats(user_id: int, days: int = 30) -> list[dict]:
    """Статистика по дням недели."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    TO_CHAR(record_date, 'Day') AS weekday,
                    EXTRACT(DOW FROM record_date) AS dow,
                    ROUND(AVG(mood), 2)        AS avg_mood,
                    ROUND(AVG(work_hours), 2)  AS avg_work,
                    ROUND(AVG(sleep_hours), 2) AS avg_sleep,
                    COUNT(*)                   AS records
                FROM daily_records
                WHERE user_id = %s
                  AND record_date >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY weekday, dow
                ORDER BY dow;
            """, (user_id, days))
            return cur.fetchall()
    finally:
        conn.close()


def get_all_users() -> list[dict]:
    """Возвращает всех пользователей (для напоминаний)."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT user_id, remind_hour FROM users;")
            return cur.fetchall()
    finally:
        conn.close()