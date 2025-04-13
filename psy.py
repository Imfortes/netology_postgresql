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

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()
            self._is_connected = False
            print("Соединение закрыто")

    def _execute(self, query, params=None, fetch=False):
        if not self._is_connected and not self.connect():
            return None

        cur = None
        try:
            cur = self.conn.cursor()
            cur.execute(query, params or ())

            if fetch:
                return cur.fetchall()
            else:
                self.conn.commit()
                return True

        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Ошибка выполнения запроса: {e}")
            return None
        finally:
            if cur:
                cur.close()

    def create_client(self, first_name, last_name, email, phone=None):
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

    def add_phone(self, client_id, phone):
        if not self._is_connected:
            self.connect()

        cur = None
        try:
            self.conn.autocommit = False
            cur = self.conn.cursor()
            cur.execute("SELECT version();")
            print(f'Подключено к: {cur.fetchone()[0]}')

            cur.execute("""
                UPDATE clients
                SET phone = %s
                WHERE id = %s;
            """, (phone, client_id))

            self.conn.commit()
            print(f'Добавлен номер телефона: {phone} клиента: {client_id}. Статус: {cur.statusmessage}')

        except psycopg2.Error as e:
            print(f'Ошибка добавления телефона к существующему клиенту {e}')


    def client_update(self, client_id, first_name, last_name, email, phone):
        if not self._is_connected:
            self.connect()

        cur = None
        try:
            self.conn.autocommit = False
            cur = self.conn.cursor()
            cur.execute("SELECT version();")
            print(f'Подключено к: {cur.fetchone()[0]}')

            cur.execute("""
                UPDATE clients
                SET first_name = %s, last_name = %s, email = %s, phone = %s
                WHERE id = %s;
            """, (first_name, last_name, email, phone, client_id))

            self.conn.commit()
            print(f'Обновлена информация о клиенте {client_id}')

        except psycopg2.Error as e:
            print(f'Ошибка обновления клиента {e}')


    def delete_phone(self, client_id):
        if not self._is_connected:
            self.connect()

        cur = None
        try:
            self.conn.autocommit = False
            cur = self.conn.cursor()
            cur.execute("SELECT version();")
            print(f'Подключено к: {cur.fetchone()[0]}')

            cur.execute("""
                UPDATE clients
                SET phone = NULL
                WHERE id = %s;
            """, (client_id,))

            updated_client = cur.fetchone()
            if updated_client:
                self.conn.commit()
                print(f"Телефон удален у клиента: ID {updated_client[0]}, {updated_client[1]} {updated_client[2]}")
                return True
            else:
                self.conn.rollback()
                print(f"Клиент с ID {client_id} не найден")
                return False

        except psycopg2.Error as e:
            print(f'Ошибка {e}')



    def delete_client(self, client_id):
        print(f'Удаление клиента № {client_id}')
        return self._execute(
            "DELETE FROM clients WHERE id = %s",
            (client_id,)
        )



    def search_client(self, client_id):
        if not self._is_connected:
            self.connect()

        cur = None
        try:
            self.conn.autocommit = False
            cur = self.conn.cursor()
            cur.execute("SELECT version();")
            print(f'Подключено к: {cur.fetchone()[0]}')

            cur.execute("""
                        SELECT id, first_name, last_name, email, phone 
                        FROM clients 
                        WHERE id = %s;
                    """, (client_id,))

            self.conn.commit()
            print(f'Клиент {client_id} найден')

        except psycopg2.Error as e:
            print(f'Ошибка : {e}')


if __name__ == "__main__":
    db = DB("", "postgres", "", "localhost", "5432")
    try:
        db.connect()
        db.create_table()
        db.create_client('Александр', 'З', 'imfo32@list.ru', '8-925-202-33-31')
        db.create_client('Ivan', 'Z', 'imfo41@list.ru', '8-925-345-35-31')
        db.create_client('Petr', 'A', 'imfor123@list.ru', '8-925-245-71-31')
        db.create_client('Sasha', 'V', 'imfo745@list.ru', '8-925-789-43-31')
        db.create_client('Edge', 'Ev', 'edge32@list.ru', '8-925-564-75-31')
        db.create_client('Edg', 'Ef', 'edge02@list.ru', '8-925-247-54-31')
        db.create_client('Edgea', 'Ed', 'edge21@list.ru', '8-925-423-23-31')
        db.create_client('Edgeas', 'Es', 'edge33@list.ru', '8-925-486-70-31')
        db.create_client('Edgease', 'Ea', 'edge32@list.ru', '8-925-024-98-31')
        db.create_client('Edgeasc', 'Eb', 'edge123@list.ru', '8-925-0345-78-31')
        # db.create_client('Александр', 'Завершнев', 'imfortes@list.ru', '8-925-205-35-31')
        db.create_client('Alex', 'Zaversh', 'imf045@list.ru', '')
        db.add_phone(8, '8-925-345-78-31')
        db.client_update(8, 'Lex', 'Zav', 'imfo756@vk.com', '8-925-345-05-31')
        db.delete_phone(8)
        db.delete_client(19)
        db.search_client(20)

    except Exception as e:
        print(f'Ошибка {e}')
    finally:
        db.conn.close()
