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
        if os.environ.get('DATABASE_URL'):
            return psycopg2.connect(os.environ.get('DATABASE_URL'))
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

    def get_pass_by_id(self, pass_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT 
                    mp.id, mp.beauty_title, mp.title, mp.other_titles, mp.connect,
                    mp.latitude, mp.longitude, mp.height, 
                    mp.winter_level, mp.summer_level, mp.autumn_level, mp.spring_level,
                    mp.images, mp.status, mp.created_at,
                    u.email, u.phone, u.fam, u.name, u.otc
                FROM mountain_passes mp
                JOIN users u ON mp.user_id = u.id
                WHERE mp.id = %s
            ''', (pass_id,))

            result = cursor.fetchone()
            if not result:
                return None

            pass_data = {
                'id': result[0],
                'beautyTitle': result[1],
                'title': result[2],
                'other_titles': result[3],
                'connect': result[4],
                'coords': {
                    'latitude': str(result[5]),
                    'longitude': str(result[6]),
                    'height': str(result[7])
                },
                'level': {
                    'winter': result[8],
                    'summer': result[9],
                    'autumn': result[10],
                    'spring': result[11]
                },
                'images': result[12],
                'status': result[13],
                'add_time': result[14].isoformat() if result[14] else '',
                'user': {
                    'email': result[15],
                    'phone': result[16],
                    'fam': result[17],
                    'name': result[18],
                    'otc': result[19]
                }
            }
            return pass_data
        finally:
            cursor.close()
            conn.close()

    def update_mountain_pass(self, pass_id: int, data: dict):
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT status FROM mountain_passes WHERE id = %s', (pass_id,))
            result = cursor.fetchone()

            if not result:
                return False, "Перевал не найден"

            if result[0] != 'new':
                return False, "Можно редактировать только перевалы со статусом 'new'"

            cursor.execute('''
                UPDATE mountain_passes 
                SET beauty_title = %s, title = %s, other_titles = %s, connect = %s,
                    latitude = %s, longitude = %s, height = %s,
                    winter_level = %s, summer_level = %s, autumn_level = %s, spring_level = %s,
                    images = %s
                WHERE id = %s
            ''', (
                data.get('beautyTitle', ''),
                data.get('title', ''),
                data.get('other_titles', ''),
                data.get('connect', ''),
                data.get('coords', {}).get('latitude'),
                data.get('coords', {}).get('longitude'),
                data.get('coords', {}).get('height'),
                data.get('level', {}).get('winter', ''),
                data.get('level', {}).get('summer', ''),
                data.get('level', {}).get('autumn', ''),
                data.get('level', {}).get('spring', ''),
                json.dumps(data.get('images', {})),
                pass_id
            ))

            conn.commit()
            return True, "Успешно обновлено"

        except Exception as e:
            conn.rollback()
            return False, f"Ошибка при обновлении: {str(e)}"
        finally:
            cursor.close()
            conn.close()

    def get_passes_by_user_email(self, email: str):
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT 
                    mp.id, mp.beauty_title, mp.title, mp.other_titles, mp.connect,
                    mp.latitude, mp.longitude, mp.height, 
                    mp.winter_level, mp.summer_level, mp.autumn_level, mp.spring_level,
                    mp.images, mp.status, mp.created_at
                FROM mountain_passes mp
                JOIN users u ON mp.user_id = u.id
                WHERE u.email = %s
                ORDER BY mp.created_at DESC
            ''', (email,))

            passes = []
            for result in cursor.fetchall():
                pass_data = {
                    'id': result[0],
                    'beautyTitle': result[1],
                    'title': result[2],
                    'other_titles': result[3],
                    'connect': result[4],
                    'coords': {
                        'latitude': str(result[5]),
                        'longitude': str(result[6]),
                        'height': str(result[7])
                    },
                    'level': {
                        'winter': result[8],
                        'summer': result[9],
                        'autumn': result[10],
                        'spring': result[11]
                    },
                    'images': result[12],
                    'status': result[13],
                    'add_time': result[14].isoformat() if result[14] else ''
                }
                passes.append(pass_data)

            return passes
        finally:
            cursor.close()
            conn.close()

    def get_passes_by_status(self, status=None):
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if status:
                cursor.execute('''
                    SELECT mp.*, u.email, u.name, u.phone 
                    FROM mountain_passes mp
                    JOIN users u ON mp.user_id = u.id
                    WHERE mp.status = %s
                    ORDER BY mp.created_at DESC
                ''', (status,))
            else:
                cursor.execute('''
                    SELECT mp.*, u.email, u.name, u.phone 
                    FROM mountain_passes mp
                    JOIN users u ON mp.user_id = u.id
                    ORDER BY mp.created_at DESC
                ''')

            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def update_pass_status(self, pass_id, status, moderator_comment=None):
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE mountain_passes 
                SET status = %s 
                WHERE id = %s
            ''', (status, pass_id))

            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()