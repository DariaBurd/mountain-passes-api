import psycopg2
import json
import os
from dotenv import load_dotenv

load_dotenv()


class DatabaseManager:
    def __init__(self):
        self.db_params = {
            'host': os.environ.get('FSTR_DB_HOST', 'localhost'),
            'port': os.environ.get('FSTR_DB_PORT', '5432'),
            'database': os.environ.get('FSTR_DB_DATABASE', 'mountain_passes'),
            'user': os.environ.get('FSTR_DB_LOGIN', 'postgres'),
            'password': os.environ.get('FSTR_DB_PASS', 'password')
        }

    def get_connection(self):
        return psycopg2.connect(**self.db_params)

    def add_mountain_pass(self, data):
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            user_data = data.get('user', {})
            pass_data = data

            cursor.execute('''
                INSERT INTO users (email, phone, fam, name, otc) 
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (email) DO NOTHING
            ''', (
                user_data.get('email'),
                user_data.get('phone'),
                user_data.get('fam'),
                user_data.get('name'),
                user_data.get('otc')
            ))

            cursor.execute('SELECT id FROM users WHERE email = %s', (user_data.get('email'),))
            result = cursor.fetchone()
            user_id = result[0] if result else None

            cursor.execute('''
                INSERT INTO mountain_passes 
                (user_id, beauty_title, title, other_titles, connect, 
                 latitude, longitude, height, winter_level, summer_level, 
                 autumn_level, spring_level, images)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                user_id,
                pass_data.get('beautyTitle', ''),
                pass_data.get('title', ''),
                pass_data.get('other_titles', ''),
                pass_data.get('connect', ''),
                pass_data.get('coords', {}).get('latitude'),
                pass_data.get('coords', {}).get('longitude'),
                pass_data.get('coords', {}).get('height'),
                pass_data.get('level', {}).get('winter', ''),
                pass_data.get('level', {}).get('summer', ''),
                pass_data.get('level', {}).get('autumn', ''),
                pass_data.get('level', {}).get('spring', ''),
                json.dumps(pass_data.get('images', {}))
            ))

            pass_id = cursor.fetchone()[0]
            conn.commit()
            return pass_id

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()