import customtkinter as ctk
from tkinter import ttk
from datetime import datetime

from db import init_db
from models import get_assignments, get_courses


ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Study Planner")
app.geometry("1000x600")


# ---------- Sidebar ----------
sidebar = ctk.CTkFrame(app, width=200)
sidebar.pack(side="left", fill="y", padx=10, pady=10)

title = ctk.CTkLabel(sidebar, text="Study Planner", font=("Arial", 22))
title.pack(pady=10)

btn_assignments = ctk.CTkButton(sidebar, text="Assignments")
btn_assignments.pack(fill="x", pady=5)

btn_courses = ctk.CTkButton(sidebar, text="Courses")
btn_courses.pack(fill="x", pady=5)


# ---------- Main Content ----------
content = ctk.CTkFrame(app)
content.pack(side="left", fill="both", expand=True, padx=10, pady=10)

content_label = ctk.CTkLabel(content, text="Assignments", font=("Arial", 18))
content_label.pack(pady=15)


# ---------- Assignment Table ----------
table = ttk.Treeview(
    content,
    columns=("title", "course", "due", "priority"),
    show="headings",
    height=14
)

table.heading("title", text="Title")
table.heading("course", text="Course")
table.heading("due", text="Due Date")
table.heading("priority", text="Priority")

table.column("title", width=260)
table.column("course", width=180)
table.column("due", width=140)
table.column("priority", width=120)

table.pack(fill="both", expand=True, padx=10, pady=10)


# ---------- Load table ----------
def load_table():
    table.delete(*table.get_children())

    for title, course, due, priority in get_assignments():
        # convert stored date -> display date
        if due:
            try:
                d = datetime.strptime(due, "%Y-%m-%d")
                due_display = d.strftime("%d/%m/%y")
            except:
                due_display = due
        else:
            due_display = ""

        table.insert("", "end", values=(title, course, due_display, priority))


# ---------- Add Assignment Popup ----------
def open_add_assignment():
    from models import add_assignment, add_course

    popup = ctk.CTkToplevel(app)
    popup.title("Add Assignment")
    popup.geometry("420x450")

    ctk.CTkLabel(popup, text="Title").pack(pady=5)
    entry_title = ctk.CTkEntry(popup, width=260)
    entry_title.pack()

    # ---- course dropdown ----
    ctk.CTkLabel(popup, text="Course").pack(pady=5)

    course_list = [c[1] for c in get_courses()]
    course_list.append("➕ Add new course")

    course_var = ctk.StringVar(value=course_list[0] if course_list else "➕ Add new course")
    dropdown = ctk.CTkOptionMenu(popup, values=course_list, variable=course_var)
    dropdown.pack()

    # input box shows ONLY if "add new course" chosen
    entry_new_course = ctk.CTkEntry(popup, width=260)
    

    def on_course_change(choice):
        if choice == "➕ Add new course":
            entry_new_course.pack(pady=5)
        else:
            entry_new_course.pack_forget()

    dropdown.configure(command=on_course_change)

    # ---- due date ----
    ctk.CTkLabel(popup, text="Due Date (DD/MM/YY)").pack(pady=5)
    entry_due = ctk.CTkEntry(popup, width=260)
    entry_due.pack()

    # ---- priority ----
    ctk.CTkLabel(popup, text="Priority (1-5)").pack(pady=5)
    entry_priority = ctk.CTkEntry(popup, width=260)
    entry_priority.pack()

    def save():
        title = entry_title.get()
        selected = course_var.get()
        new_course = entry_new_course.get()
        due_input = entry_due.get().strip()
        priority = entry_priority.get() or 1

        # convert date
        due_for_db = ""
        if due_input:
            try:
                d = datetime.strptime(due_input, "%d/%m/%y")
                due_for_db = d.strftime("%Y-%m-%d")
            except:
                due_for_db = due_input

        # resolve course id
        if selected == "➕ Add new course":
            if new_course:
                add_course(new_course)
                course_id = get_courses()[-1][0]
            else:
                course_id = None
        else:
            for c in get_courses():
                if c[1] == selected:
                    course_id = c[0]

        add_assignment(title, course_id, due_for_db, int(priority))
        load_table()
        popup.destroy()

    ctk.CTkButton(popup, text="Save", command=save).pack(pady=15)


add_btn = ctk.CTkButton(content, text="Add Assignment", command=open_add_assignment)
add_btn.pack(pady=10)


# ---------- Startup ----------
init_db()
load_table()

app.mainloop()
