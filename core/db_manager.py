import sqlite3
import os

class DBManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_db_dir()
        self._init_db()

    def _ensure_db_dir(self):
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS subdomains(
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           domain TEXT UNIQUE,
                           target TEXT,
                           found_at DATETIME DEFAULT CURRENT_TIMESTAMP
                           )
            """)
            conn.commit()

    def filter_new_subdomains(self, domain_list: list, target: str) -> list:
        new_found = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for domain in domain_list:
                try:
                    cursor.execute("INSERT INTO subdomains (domain, target) VALUES (?, ?)", (domain.strip().lower(), target))
                    new_found.append(domain)
                except sqlite3.IntegrityError:
                    continue
            conn.commit()
        return new_found

    