import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    if os.environ.get('DATABASE_URL'):
        return psycopg2.connect(os.environ.get('DATABASE_URL'))

    return psycopg2.connect(
        host=os.environ.get('FSTR_DB_HOST', 'localhost'),
        port=os.environ.get('FSTR_DB_PORT', '5432'),
        database=os.environ.get('FSTR_DB_DATABASE', 'mountain_passes'),
        user=os.environ.get('FSTR_DB_LOGIN', 'postgres'),
        password=os.environ.get('FSTR_DB_PASS', 'password')
    )


def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
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
        print("✅ Таблицы созданы успешно!")

    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    init_database()