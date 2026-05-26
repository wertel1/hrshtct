
CREATE TABLE IF NOT EXISTS users (
    user_id     BIGINT PRIMARY KEY,
    username    VARCHAR(255),
    first_name  VARCHAR(255),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    remind_hour INTEGER DEFAULT 21       
);

COMMENT ON TABLE users IS 'Зарегистрированные пользователи бота';
COMMENT ON COLUMN users.remind_hour IS 'Час дня для отправки напоминания (UTC)';

CREATE TABLE IF NOT EXISTS daily_records (
    id           SERIAL PRIMARY KEY,
    user_id      BIGINT NOT NULL
                     REFERENCES users(user_id) ON DELETE CASCADE,
    record_date  DATE NOT NULL DEFAULT CURRENT_DATE,
    mood         INTEGER NOT NULL
                     CHECK (mood BETWEEN 1 AND 5),
    work_hours   NUMERIC(4,1) NOT NULL
                     CHECK (work_hours >= 0 AND work_hours <= 24),
    sleep_hours  NUMERIC(4,1) NOT NULL
                     CHECK (sleep_hours >= 0 AND sleep_hours <= 24),
    comment      TEXT,                       
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  
    CONSTRAINT uq_user_date UNIQUE (user_id, record_date)
);

COMMENT ON TABLE daily_records IS 'Ежедневные записи настроения и показателей';
COMMENT ON COLUMN daily_records.mood        IS 'Оценка настроения от 1 (плохо) до 5 (отлично)';
COMMENT ON COLUMN daily_records.work_hours  IS 'Часы продуктивной работы или учёбы';
COMMENT ON COLUMN daily_records.sleep_hours IS 'Часы сна в предыдущую ночь';

CREATE INDEX IF NOT EXISTS idx_records_user_date
    ON daily_records (user_id, record_date DESC);


CREATE INDEX IF NOT EXISTS idx_records_mood
    ON daily_records (mood);

CREATE INDEX IF NOT EXISTS idx_records_date
    ON daily_records (record_date);