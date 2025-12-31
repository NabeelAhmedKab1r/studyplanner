import sqlite3

DB_NAME = "planner.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            course_id INTEGER,
            due_date TEXT,
            priority INTEGER,
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
    """)

    conn.commit()
    conn.close()
