import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime

from models import (
    get_assignments,
    get_courses,
    toggle_completed,
    delete_assignment,
    update_assignment,
    add_assignment,
    add_course
)


def build_assignments_page(app, main):

    # ---------------- FILTER STATE ----------------
    search_var = ctk.StringVar()

    def load_table():
        table.delete(*table.get_children())

        query = search_var.get().lower().strip()

        for row in get_assignments():
            _id, title, course, due, priority, done = row

            # ---------- SEARCH FILTER ----------
            text = f"{title} {course}".lower()
            if query and query not in text:
                continue

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

    # ---------------- TABLE ACTIONS ----------------
    def on_row_double_click(event):
        selected = table.focus()
        if selected:
            toggle_completed(int(selected))
            load_table()

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

    # ---------------- POPUPS ----------------
    def open_add_popup(app, main):
        popup = ctk.CTkToplevel(app)
        popup.title("Add Assignment")
        popup.geometry("420x450")

        ctk.CTkLabel(popup, text="Title").pack(pady=5)
        entry_title = ctk.CTkEntry(popup, width=260)
        entry_title.pack()

        ctk.CTkLabel(popup, text="Course").pack(pady=5)

        course_list = [c[1] for c in get_courses()] + ["➕ Add new course"]
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
                course_id = next(c[0] for c in get_courses() if c[1] == selected)

            add_assignment(title, course_id, due_for_db, int(priority))
            popup.destroy()
            load_table()

        ctk.CTkButton(popup, text="Save", command=save).pack(pady=10)

    def open_edit_popup(assign_id):
        r = [r for r in get_assignments() if r[0] == assign_id][0]
        _, title, course, due, priority, _ = r

        popup = ctk.CTkToplevel(app)
        popup.title("Edit Assignment")
        popup.geometry("420x450")

        ctk.CTkLabel(popup, text="Title").pack(pady=5)
        entry_title = ctk.CTkEntry(popup, width=260)
        entry_title.insert(0, title)
        entry_title.pack()

        ctk.CTkLabel(popup, text="Course").pack(pady=5)

        course_list = [c[1] for c in get_courses()] + ["➕ Add new course"]
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
                course_id = next(c[0] for c in get_courses() if c[1] == selected)

            update_assignment(assign_id, new_title, course_id, due_for_db, int(new_priority))
            popup.destroy()
            load_table()

        ctk.CTkButton(popup, text="Save Changes", command=save).pack(pady=10)

    # ---------------- PAGE LAYOUT ----------------
    for widget in main.winfo_children():
        widget.destroy()

    ctk.CTkLabel(main, text="Assignments",
                 font=("Arial", 22, "bold")).pack(pady=15)

    # SEARCH BAR
    search_frame = ctk.CTkFrame(main, fg_color="transparent")
    search_frame.pack(pady=5)

    ctk.CTkLabel(search_frame, text="Search:").pack(side="left", padx=5)

    search_entry = ctk.CTkEntry(search_frame, textvariable=search_var, width=220)
    search_entry.pack(side="left", padx=5)

    # update table whenever typing
    search_entry.bind("<KeyRelease>", lambda e: load_table())

    # BUTTONS
    button_bar = ctk.CTkFrame(main, fg_color="transparent")
    button_bar.pack(pady=5)

    ctk.CTkButton(button_bar, text="Add Assignment",
                  command=lambda: open_add_popup(app, main)).pack(side="left", padx=5)

    ctk.CTkButton(button_bar, text="Edit Selected",
                  command=edit_selected).pack(side="left", padx=5)

    ctk.CTkButton(button_bar, text="Delete Selected",
                  command=delete_selected).pack(side="left", padx=5)

    # TABLE
    table_frame = ctk.CTkFrame(main, corner_radius=10)
    table_frame.pack(fill="both", expand=True, padx=15, pady=10)

    global table
    table = ttk.Treeview(
        table_frame,
        columns=("title", "course", "due", "priority", "completed"),
        show="headings",
        height=16,
    )

    table.heading("title", text="Title")
    table.heading("course", text="Course")
    table.heading("due", text="Due Date")
    table.heading("priority", text="Priority")
    table.heading("completed", text="Completed")

    table.pack(fill="both", expand=True)

    table.tag_configure("overdue", background="#3a1818", foreground="#ff8888")
    table.tag_configure("soon", background="#3a3318", foreground="#ffe28a")

    table.bind("<Double-1>", on_row_double_click)

    load_table()
