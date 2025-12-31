from db import get_connection

def add_course(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO courses (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def get_courses():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM courses")
    rows = cur.fetchall()
    conn.close()
    return rows

def add_assignment(title, course_id, due_date, priority):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO assignments (title, course_id, due_date, priority) VALUES (?, ?, ?, ?)",
        (title, course_id, due_date, priority)
    )
    conn.commit()
    conn.close()

def get_upcoming_assignments():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id, a.title, c.name, a.due_date, a.priority, a.completed
        FROM assignments a
        LEFT JOIN courses c ON a.course_id = c.id
        ORDER BY a.due_date
    """)
    rows = cur.fetchall()
    conn.close()
    return rows
