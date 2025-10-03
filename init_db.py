import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def get_db_params():
    return {
        'host': os.environ.get('FSTR_DB_HOST', 'localhost'),
        'port': os.environ.get('FSTR_DB_PORT', '5432'),
        'database': 'postgres',
        'user': os.environ.get('FSTR_DB_LOGIN', 'postgres'),
        'password': os.environ.get('FSTR_DB_PASS', 'password')
    }


def init_database():
    conn = psycopg2.connect(**get_db_params())
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        cursor.execute("CREATE DATABASE mountain_passes")
        print("База данных mountain_passes создана")
    except Exception as e:
        print(f"База данных уже существует: {e}")
    finally:
        cursor.close()
        conn.close()

    db_params = get_db_params()
    db_params['database'] = 'mountain_passes'
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            fam TEXT,
            name TEXT NOT NULL,
            otc TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mountain_passes (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            beauty_title TEXT,
            title TEXT NOT NULL,
            other_titles TEXT,
            connect TEXT,
            latitude REAL,
            longitude REAL,
            height INTEGER,
            winter_level TEXT,
            summer_level TEXT,
            autumn_level TEXT,
            spring_level TEXT,
            images JSONB,
            status TEXT NOT NULL DEFAULT 'new' 
                CHECK (status IN ('new', 'pending', 'accepted', 'rejected')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    cursor.close()
    conn.close()
    print("Таблицы созданы успешно!")


if __name__ == '__main__':
    init_database()