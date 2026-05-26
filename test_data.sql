


INSERT INTO users (user_id, username, first_name, remind_hour)
VALUES (123456789, 'test_user', 'Алексей', 21)
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO daily_records (user_id, record_date, mood, work_hours, sleep_hours, comment)
VALUES
    (8108522195, CURRENT_DATE - 0,  4, 6.0,  7.5, 'Хороший рабочий день, успел многое'),
    (8108522195, CURRENT_DATE - 1,  3, 4.5,  6.0, 'Немного устал, голова болит'),
    (8108522195, CURRENT_DATE - 2,  5, 7.0,  8.0, 'Отличный день! Всё получилось'),
    (8108522195, CURRENT_DATE - 3,  2, 2.0,  5.5, 'Плохо спал, ничего не успел'),
    (8108522195, CURRENT_DATE - 4,  4, 5.5,  7.0, NULL),
    (8108522195, CURRENT_DATE - 5,  3, 3.0,  9.0, 'Выходной, расслаблялся'),
    (8108522195, CURRENT_DATE - 6,  4, 8.0,  7.5, 'Много работал, но доволен'),
    (8108522195, CURRENT_DATE - 8,  1, 1.0,  4.5, 'Ужасный день, заболел'),
    (8108522195, CURRENT_DATE - 9,  2, 0.5,  10.0,'Болел, весь день спал'),
    (8108522195, CURRENT_DATE - 10, 3, 4.0,  8.0, 'Постепенно прихожу в норму'),
    (8108522195, CURRENT_DATE - 12, 5, 6.5,  8.5, 'Прекрасный день, гулял и работал'),
    (8108522195, CURRENT_DATE - 15, 4, 5.0,  7.0, NULL),
    (8108522195, CURRENT_DATE - 18, 3, 3.5,  6.5, 'Средненький день'),
    (8108522195, CURRENT_DATE - 22, 5, 7.0,  8.0, 'Завершил большой проект!'),
    (123456789, CURRENT_DATE - 28, 2, 2.0,  5.0, 'Стресс, дедлайн горит')
ON CONFLICT (user_id, record_date) DO NOTHING;