import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime

from db import init_db
from models import (
    get_assignments,
    get_courses,
    toggle_completed,
    delete_assignment,
    update_assignment,
    add_assignment,
    add_course
)


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Study Planner")
app.geometry("1150x680")


# ---------- Sidebar ----------
sidebar = ctk.CTkFrame(app, width=220, corner_radius=15)
sidebar.pack(side="left", fill="y", padx=15, pady=15)

ctk.CTkLabel(
    sidebar,
    text="Study Planner",
    font=("Arial", 26, "bold")
).pack(pady=20)


# (buttons – now inside sidebar)
def delete_selected():
    selected = table.focus()
    if not selected:
        messagebox.showwarning("Select something", "Choose an assignment first.")
        return
    if messagebox.askyesno("Delete", "Delete selected assignment?"):
        delete_assignment(int(selected))
        load_table()


def edit_selected():
    selected = table.focus()
    if not selected:
        messagebox.showwarning("Select something", "Choose an assignment first.")
        return
    open_edit_popup(int(selected))


ctk.CTkButton(
    sidebar,
    text="Add Assignment",
    command=lambda: open_add_popup(),
    width=180
).pack(pady=10)

ctk.CTkButton(
    sidebar,
    text="Edit Selected",
    command=edit_selected,
    width=180
).pack(pady=10)

ctk.CTkButton(
    sidebar,
    text="Delete Selected",
    command=delete_selected,
    width=180
).pack(pady=10)


# ---------- Main Area ----------
main = ctk.CTkFrame(app, corner_radius=15)
main.pack(side="left", fill="both", expand=True, padx=15, pady=15)

ctk.CTkLabel(
    main,
    text="Assignments",
    font=("Arial", 22, "bold")
).pack(pady=15)


# ---------- Table ----------
table_frame = ctk.CTkFrame(main, corner_radius=10)
table_frame.pack(fill="both", expand=True, padx=15, pady=10)

table = ttk.Treeview(
    table_frame,
    columns=("title", "course", "due", "priority", "completed"),
    show="headings",
    height=16
)

table.heading("title", text="Title")
table.heading("course", text="Course")
table.heading("due", text="Due Date")
table.heading("priority", text="Priority")
table.heading("completed", text="Completed")

table.column("title", width=270)
table.column("course", width=160)
table.column("due", width=130)
table.column("priority", width=90)
table.column("completed", width=110)

table.pack(fill="both", expand=True, pady=5, padx=5)


# ---------- Load Table ----------
def load_table():
    table.delete(*table.get_children())

for row in get_assignments():
    _id, title, course, due, priority, done = row

    due_display = ""
    tag = ""

    if due:
        try:
            d = datetime.strptime(due, "%Y-%m-%d")
            due_display = d.strftime("%d/%m/%y")

            today = datetime.today().date()
            diff = (d.date() - today).days

            if diff < 0:
                tag = "overdue"
            elif diff <= 3:
                tag = "soon"

        except:
            due_display = due

    table.insert(
        "",
        "end",
        iid=_id,
        values=(title, course, due_display, priority, "✔" if done else ""),
        tags=(tag,)
    )



# ---------- Toggle Completed ----------
def on_row_double_click(event):
    selected = table.focus()
    if selected:
        toggle_completed(int(selected))
        load_table()


table.bind("<Double-1>", on_row_double_click)


# ---------- Add Popup ----------
def open_add_popup():
    popup = ctk.CTkToplevel(app)
    popup.title("Add Assignment")
    popup.geometry("420x450")

    ctk.CTkLabel(popup, text="Title").pack(pady=5)
    entry_title = ctk.CTkEntry(popup, width=260)
    entry_title.pack()

    ctk.CTkLabel(popup, text="Course").pack(pady=5)

    course_list = [c[1] for c in get_courses()]
    course_list.append("➕ Add new course")

    course_var = ctk.StringVar(value=course_list[0])
    dropdown = ctk.CTkOptionMenu(popup, values=course_list, variable=course_var)
    dropdown.pack()

    entry_new_course = ctk.CTkEntry(popup, width=260)

    def on_course_change(choice):
        if choice == "➕ Add new course":
            entry_new_course.pack(pady=5)
        else:
            entry_new_course.pack_forget()

    dropdown.configure(command=on_course_change)

    ctk.CTkLabel(popup, text="Due (DD/MM/YY)").pack(pady=5)
    entry_due = ctk.CTkEntry(popup, width=260)
    entry_due.pack()

    ctk.CTkLabel(popup, text="Priority (1-5)").pack(pady=5)
    entry_priority = ctk.CTkEntry(popup, width=260)
    entry_priority.pack()

    def save():
        selected = course_var.get()
        new_course = entry_new_course.get()
        title = entry_title.get()
        due_input = entry_due.get()
        priority = entry_priority.get() or 1

        due_for_db = ""
        if due_input:
            try:
                d = datetime.strptime(due_input, "%d/%m/%y")
                due_for_db = d.strftime("%Y-%m-%d")
            except:
                due_for_db = due_input

        if selected == "➕ Add new course":
            add_course(new_course)
            course_id = get_courses()[-1][0]
        else:
            course_id = None
            for c in get_courses():
                if c[1] == selected:
                    course_id = c[0]

        add_assignment(title, course_id, due_for_db, int(priority))
        popup.destroy()
        load_table()

    ctk.CTkButton(popup, text="Save", command=save).pack(pady=10)


# ---------- Edit Popup ----------
def open_edit_popup(assign_id):
    records = get_assignments()
    record = [r for r in records if r[0] == assign_id][0]

    _, title, course, due, priority, _ = record

    popup = ctk.CTkToplevel(app)
    popup.title("Edit Assignment")
    popup.geometry("420x450")

    ctk.CTkLabel(popup, text="Title").pack(pady=5)
    entry_title = ctk.CTkEntry(popup, width=260)
    entry_title.insert(0, title)
    entry_title.pack()

    ctk.CTkLabel(popup, text="Course").pack(pady=5)

    course_list = [c[1] for c in get_courses()]
    course_list.append("➕ Add new course")

    course_var = ctk.StringVar(value=course)
    dropdown = ctk.CTkOptionMenu(popup, values=course_list, variable=course_var)
    dropdown.pack()

    entry_new_course = ctk.CTkEntry(popup, width=260)

    def on_course_change(choice):
        if choice == "➕ Add new course":
            entry_new_course.pack(pady=5)
        else:
            entry_new_course.pack_forget()

    dropdown.configure(command=on_course_change)

    ctk.CTkLabel(popup, text="Due (DD/MM/YY)").pack(pady=5)
    entry_due = ctk.CTkEntry(popup, width=260)
    if due:
        entry_due.insert(0, datetime.strptime(due, "%Y-%m-%d").strftime("%d/%m/%y"))
    entry_due.pack()

    ctk.CTkLabel(popup, text="Priority (1-5)").pack(pady=5)
    entry_priority = ctk.CTkEntry(popup, width=260)
    entry_priority.insert(0, str(priority))
    entry_priority.pack()

    def save():
        new_title = entry_title.get()
        selected = course_var.get()
        new_course = entry_new_course.get()
        due_input = entry_due.get()
        new_priority = entry_priority.get()

        due_for_db = ""
        if due_input:
            try:
                d = datetime.strptime(due_input, "%d/%m/%y")
                due_for_db = d.strftime("%Y-%m-%d")
            except:
                due_for_db = due_input

        if selected == "➕ Add new course":
            add_course(new_course)
            course_id = get_courses()[-1][0]
        else:
            course_id = None
            for c in get_courses():
                if c[1] == selected:
                    course_id = c[0]

        update_assignment(assign_id, new_title, course_id, due_for_db, int(new_priority))
        popup.destroy()
        load_table()

    ctk.CTkButton(popup, text="Save Changes", command=save).pack(pady=10)


# ---------- Startup ----------
init_db()
load_table()

app.mainloop()
