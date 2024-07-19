import sqlite3
import threading
from queue import Queue

class Database:
    def __init__(self, db_path, pool_size=5):
        self.db_path = db_path
        self.pool_size = pool_size
        self.pool = Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        self._initialize_pool()

    def _initialize_pool(self):
        for _ in range(self.pool_size):
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.pool.put(conn)

    def _get_connection(self):
        with self.lock:
            return self.pool.get()

    def _return_connection(self, conn):
        with self.lock:
            self.pool.put(conn)

    def open(self):
        return self._get_connection()

    def close(self, conn):
        self._return_connection(conn)

    def execute(self, query, params=None):
        conn = self.open()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
        finally:
            self.close(conn)

    def fetchone(self, query, params=None):
        conn = self.open()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchone()
        finally:
            self.close(conn)

    def fetchall(self, query, params=None):
        conn = self.open()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        finally:
            self.close(conn)
