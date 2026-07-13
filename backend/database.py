import sqlite3
from contextlib import contextmanager

DB_PATH = "dashboard.db"

def init_db():
    """Kreira tabele ako ne postoje. Poziva se jednom pri pokretanju app-a."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hranjenja (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ko_je_hranio TEXT NOT NULL,
            vreme TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS poslovi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            naziv TEXT NOT NULL,
            zavrsen INTEGER NOT NULL DEFAULT 0,
            kreiran TEXT NOT NULL,
            zavrsen_u TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kupovina (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artikal TEXT NOT NULL,
            kupljen INTEGER NOT NULL DEFAULT 0,
            kreiran TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@contextmanager
def get_db():
    """Context manager koji otvara konekciju, daje je endpointu, pa je sigurno zatvara."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # da rezultati liče na dict, ne na tuple
    try:
        yield conn
    finally:
        conn.close()