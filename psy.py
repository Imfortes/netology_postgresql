import psycopg2
from psycopg2 import sql
import sys

# print(sys.getdefaultencoding())

class DB:
    def __init__(self, db_name, db_user, db_password, db_host='localhost', db_port=5432):
        self.dbname = db_name
        self.user = db_user
        self.password = db_password
        self.host = db_host
        self.port = db_port

        self.clients = []
        self.conn = None
        self._is_connected = False

    def connect(self) -> None:
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            self._is_connected = True
            print(f'Успешное подключение к базе данных {self.dbname}')
        except (Exception, psycopg2.Error) as error:
            print(f'Ошибка подключения {error}')
            self._is_connected = False


    def create_table(self) -> None:
        if not self._is_connected:
            self.connect()

        try:
            self.conn.set_session(autocommit=True)
            cur = self.conn.cursor()

            cur.execute("SELECT version();")
            print(f'Подключено к: {cur.fetchone()[0]}')

            cur.execute("""
                    CREATE TABLE IF NOT EXISTS clients (
                        id SERIAL PRIMARY KEY,
                        first_name VARCHAR(50) NOT NULL,
                        last_name VARCHAR(50) NOT NULL,
                        email VARCHAR(100) UNIQUE,
                        phone VARCHAR(20),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            print(f'Статус запроса: {cur.statusmessage}')

            cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM pg_tables
                        WHERE schemaname = 'public'
                        AND tablename = 'clients'
                    );
                """)
            print(f'Таблица clients существует: {cur.fetchone()[0]}')

        except psycopg2.Error as e:
            print(f'Ошибка: {e}')
        finally:
            pass
            # cur.close()
            # self.conn.close()

    def create_client(self, first_name, last_name, email, phone):
        if not self._is_connected:
            self.connect()

        cur = None
        try:
            self.conn.autocommit = False
            cur = self.conn.cursor()

            cur.execute("SELECT version();")
            print(f'Подключено к: {cur.fetchone()[0]}')

            cur.execute("""
                        INSERT INTO clients (first_name, last_name, email, phone)
                        VALUES (%s, %s, %s, %s);
                    """, (first_name, last_name, email, phone))

            self.conn.commit()
            print(f'Клиент добавлен. Статус: {cur.statusmessage}')


        except psycopg2.IntegrityError as e:
            self.conn.rollback()
            print(f"Ошибка целостности данных: {e}")

        except (Exception, psycopg2.Error) as error:
            self.conn.rollback()
            print(f"Ошибка при добавлении клиента: {error}")

        finally:
            if cur:
                pass
                # cur.close()

    def add_phone(self, phone):
        if not self._is_connected:
            self.connect()

        cur = None
        try:
            self.conn.autocommit = False
            cur = self.conn.cursor()
            cur.execute("SELECT version();")
            print(f'Подключено к: {cur.fetchone()[0]}')

        except psycopg2.Error as e:
            print(f'Ошибка добавления телефона к существующему клиенту {e}')



if __name__ == "__main__":
    db = DB(1,"postgres", 1, "localhost","5432")
    db.create_table()
    try:
        db.connect()
        db.create_table()
        db.create_client('Alex', 'Zav', 'zav@list.ru', '8-999-999-99-9')

    except Exception as e:
        print(f'Ошибка {e}')
    finally:
        db.conn.close()
