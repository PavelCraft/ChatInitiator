import os
import sqlite3

def update_table_structure(db_name="user_profiles.db"):
    # Подключаемся к базе данных
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Добавляем новые булевые поля, если их ещё нет
    try:
        cursor.execute('ALTER TABLE profiles ADD COLUMN unread BOOLEAN')
    except sqlite3.OperationalError:
        pass  # Поле уже существует


    conn.commit()
    conn.close()

    print(f"Структура таблицы обновлена в базе данных {db_name}")


update_table_structure()
