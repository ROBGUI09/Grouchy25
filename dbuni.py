import sqlite3
import asyncio

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)

    def execute(self, query, *args):
        if not self.conn:
            self.connect()
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, args)
            self.conn.commit()
            return cursor
        except Exception as e:
            print(f"Ошибка выполнения SQL запроса: {e}")
            return None

    def fetchall(self, query, *args):
        cursor = self.execute(query, *args)
        if cursor:
            return cursor.fetchall()
        return None

    def fetchone(self, query, *args):
        cursor = self.execute(query, *args)
        if cursor:
            return cursor.fetchone()
        return None

    def close(self):
        if self.conn:
            self.conn.close()
