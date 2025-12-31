import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime

from db import init_db
from models import (
    get_assignments,
    get_courses,
    toggle_completed,
    delete_assignment,
    update_assignment
)


ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Study Planner")
app.geometry("1100x650")


# ---------- Sidebar ----------
sidebar = ctk.CTkFrame(app, width=200)
sidebar.pack(side="left", fill="y", padx=10, pady=10)

ctk.CTkLabel(sidebar, text="Study Planner", font=("Arial", 22)).pack(pady=10)


# ---------- Main Content ----------
content = ctk.CTkFrame(app)
content.pack(side="left", fill="both", expand=True, padx=10, pady=10)

ctk.CTkLabel(content, text="Assignments", font=("Arial", 18)).pack(pady=15)


# ---------- Table ----------
table = ttk.Treeview(
    content,
    columns=("title", "course", "due", "priority", "done"),
    show="headings",
    height=15
)

table.heading("title", text="Title")
table.heading("course", text="Course")
table.heading("due", text="Due Date")
table.heading("priority", text="Priority")
table.heading("done", text="Completed")

table.column("title", width=260)
table.column("course", width=160)
table.column("due", width=130)
table.column("priority", width=90)
table.column("done", width=110)

table.pack(fill="both", expand=True, padx=10, pady=10)


# ---------- Load Table ----------
def load_table():
    table.delete(*table.get_children())

    for row in get_assignments():
        _id, title, course, due, priority, done = row

        if due:
            try:
                d = datetime.strptime(due, "%Y-%m-%d")
                due_display = d.strftime("%d/%m/%y")
            except:
                due_display = due
        else:
            due_display = ""

        table.insert(
            "",
            "end",
            iid=_id,
            values=(title, course, due_display, priority, "✔" if done else "")
        )


# ---------- Toggle Complete ----------
def on_row_double_click(event):
    selected = table.focus()
    if selected:
        toggle_completed(int(selected))
        load_table()


table.bind("<Double-1>", on_row_double_click)


# ---------- Delete ----------
def delete_selected():
    selected = table.focus()
    if not selected:
        messagebox.showwarning("Select something", "Choose an assignment first.")
        return

    if messagebox.askyesno("Delete", "Are you sure you want to delete this?"):
        delete_assignment(int(selected))
        load_table()


# ---------- Edit ----------
def edit_selected():
    selected = table.focus()
    if not selected:
        messagebox.showwarning("Select something", "Choose an assignment first.")
        return

    _id, title, course, due, priority, done = None, None, None, None, None, None

    for row in get_assignments():
        if row[0] == int(selected):
            _id, title, course, due, priority, done = row

    popup = ctk.CTkToplevel(app)
    popup.title("Edit Assignment")
    popup.geometry("420x460")

    # title
    ctk.CTkLabel(popup, text="Title").pack(pady=5)
    entry_title = ctk.CTkEntry(popup, width=260)
    entry_title.insert(0, title)
    entry_title.pack()

    # course dropdown
    from models import add_course
    ctk.CTkLabel(popup, text="Course").pack(pady=5)

    course_list = [c[1] for c in get_courses()]
    course_list.append("➕ Add new course")

    course_var = ctk.StringVar(value=course or "➕ Add new course")
    dropdown = ctk.CTkOptionMenu(popup, values=course_list, variable=course_var)
    dropdown.pack()

    entry_new_course = ctk.CTkEntry(popup, width=260)

    def on_course_change(choice):
        if choice == "➕ Add new course":
            entry_new_course.pack(pady=5)
        else:
            entry_new_course.pack_forget()

    dropdown.configure(command=on_course_change)

    # due date
    ctk.CTkLabel(popup, text="Due (DD/MM/YY)").pack(pady=5)
    entry_due = ctk.CTkEntry(popup, width=260)
    if due:
        try:
            entry_due.insert(0, datetime.strptime(due, "%Y-%m-%d").strftime("%d/%m/%y"))
        except:
            entry_due.insert(0, due)
    entry_due.pack()

    # priority
    ctk.CTkLabel(popup, text="Priority (1-5)").pack(pady=5)
    entry_priority = ctk.CTkEntry(popup, width=260)
    entry_priority.insert(0, str(priority or ""))
    entry_priority.pack()

    def save_changes():
        from models import get_courses

        new_title = entry_title.get()
        selected_course = course_var.get()
        typed_new_course = entry_new_course.get()
        due_input = entry_due.get().strip()
        new_priority = entry_priority.get() or 1

        due_for_db = ""
        if due_input:
            try:
                d = datetime.strptime(due_input, "%d/%m/%y")
                due_for_db = d.strftime("%Y-%m-%d")
            except:
                due_for_db = due_input

        if selected_course == "➕ Add new course":
            if typed_new_course:
                add_course(typed_new_course)
                course_id = get_courses()[-1][0]
            else:
                course_id = None
        else:
            course_id = None
            for c in get_courses():
                if c[1] == selected_course:
                    course_id = c[0]

        update_assignment(int(selected), new_title, course_id, due_for_db, int(new_priority))

        popup.destroy()
        load_table()

    ctk.CTkButton(popup, text="Save Changes", command=save_changes).pack(pady=15)


# ---------- Buttons ----------
buttons = ctk.CTkFrame(content)
buttons.pack()

ctk.CTkButton(buttons, text="Add Assignment", command=lambda: open_add_assignment()).grid(row=0, column=0, padx=5)
ctk.CTkButton(buttons, text="Edit Selected", command=edit_selected).grid(row=0, column=1, padx=5)
ctk.CTkButton(buttons, text="Delete Selected", command=delete_selected).grid(row=0, column=2, padx=5)


# ---------- Add Popup (unchanged) ----------
def open_add_assignment():
    from models import add_assignment, add_course, get_courses

    popup = ctk.CTkToplevel(app)
    popup.title("Add Assignment")
    popup.geometry("420x450")

    ctk.CTkLabel(popup, text="Title").pack(pady=5)
    entry_title = ctk.CTkEntry(popup, width=260)
    entry_title.pack()

    ctk.CTkLabel(popup, text="Course").pack(pady=5)

    course_list = [c[1] for c in get_courses()]
    course_list.append("➕ Add new course")

    course_var = ctk.StringVar(value=course_list[0] if course_list else "➕ Add new course")
    dropdown = ctk.CTkOptionMenu(popup, values=course_list, variable=course_var)
    dropdown.pack()

    entry_new_course = ctk.CTkEntry(popup, width=260)

    def on_course_change(choice):
        if choice == "➕ Add new course":
            entry_new_course.pack(pady=5)
        else:
            entry_new_course.pack_forget()

    dropdown.configure(command=on_course_change)

    ctk.CTkLabel(popup, text="Due Date (DD/MM/YY)").pack(pady=5)
    entry_due = ctk.CTkEntry(popup, width=260)
    entry_due.pack()

    ctk.CTkLabel(popup, text="Priority (1-5)").pack(pady=5)
    entry_priority = ctk.CTkEntry(popup, width=260)
    entry_priority.pack()

    def save():
        title = entry_title.get()
        selected = course_var.get()
        new_course = entry_new_course.get()
        due_input = entry_due.get().strip()
        priority = entry_priority.get() or 1

        due_for_db = ""
        if due_input:
            try:
                d = datetime.strptime(due_input, "%d/%m/%y")
                due_for_db = d.strftime("%Y-%m-%d")
            except:
                due_for_db = due_input

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


# ---------- Startup ----------
init_db()
load_table()

app.mainloop()
