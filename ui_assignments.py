import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime

from models import (
    get_assignments, get_courses, toggle_completed,
    delete_assignment, update_assignment, add_assignment, add_course,
)

COLORS = {
    "bg":          "#0F0F17",
    "card":        "#13131F",
    "border":      "#1E1E2E",
    "accent":      "#6366F1",
    "accent_hover":"#4F46E5",
    "text":        "#E8E8F0",
    "text_muted":  "#5A5A70",
    "danger":      "#EF4444",
    "danger_hover":"#DC2626",
    "secondary":   "#1E1E2E",
    "secondary_hover": "#252535",
    "table_bg":    "#0F0F17",
    "table_card":  "#13131F",
    "table_sel":   "#23233A",
    "table_head":  "#13131F",
    "table_head_fg": "#8888A8",
    "overdue_bg":  "#201318",
    "overdue_fg":  "#E08888",
    "soon_bg":     "#1C1910",
    "soon_fg":     "#D4A855",
    "done_fg":     "#747490",
}


def _apply_table_style():
    dark = ctk.get_appearance_mode() == "Dark"
    bg      = "#0F0F17" if dark else "#F2F2F8"
    fg      = "#E8E8F0" if dark else "#1A1A2E"
    head_bg = "#13131F" if dark else "#E4E4EE"
    head_fg = "#8888A8" if dark else "#666688"
    sel_bg  = "#23233A" if dark else "#C8C8E8"
    sel_fg  = "#FFFFFF"  if dark else "#0A0A1E"

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("SP.Treeview",
        background=bg,
        foreground=fg,
        fieldbackground=bg,
        borderwidth=0,
        rowheight=38,
        font=("Helvetica Neue", 13),
    )
    style.configure("SP.Treeview.Heading",
        background=head_bg,
        foreground=head_fg,
        borderwidth=0,
        relief="flat",
        font=("Helvetica Neue", 11),
    )
    style.map("SP.Treeview",
        background=[("selected", sel_bg)],
        foreground=[("selected", sel_fg)],
    )
    style.map("SP.Treeview.Heading",
        background=[("active", head_bg)],
    )


def _popup(app, title_text, height=500):
    p = ctk.CTkToplevel(app)
    p.title(title_text)
    p.geometry(f"420x{height}")
    p.resizable(False, False)
    p.grab_set()

    ctk.CTkLabel(p, text=title_text,
                 font=("Helvetica Neue", 18, "bold")).pack(
        pady=(24, 4), padx=28, anchor="w")

    form = ctk.CTkFrame(p, fg_color="transparent")
    form.pack(fill="x", padx=28, pady=(8, 0))

    return p, form


def _field(parent, label, grid_row, default="", placeholder=""):
    ctk.CTkLabel(parent, text=label,
                 font=("Helvetica Neue", 12),
                 text_color=COLORS["text_muted"]).grid(
        row=grid_row, column=0, sticky="w", pady=(14, 2))
    e = ctk.CTkEntry(parent, width=340, height=36,
                     font=("Helvetica Neue", 13),
                     placeholder_text=placeholder)
    if default:
        e.insert(0, default)
    e.grid(row=grid_row + 1, column=0, sticky="w")
    return e


def _course_dropdown(parent, form, grid_row):
    ctk.CTkLabel(parent, text="Course",
                 font=("Helvetica Neue", 12),
                 text_color=COLORS["text_muted"]).grid(
        row=grid_row, column=0, sticky="w", pady=(14, 2))

    courses = get_courses()
    options = [c[1] for c in courses] + ["+ Add new course"]
    var = ctk.StringVar(value=options[0] if options else "+ Add new course")
    dropdown = ctk.CTkOptionMenu(form, values=options, variable=var,
                                  width=340, height=36,
                                  font=("Helvetica Neue", 13))
    dropdown.grid(row=grid_row + 1, column=0, sticky="w")

    new_lbl = ctk.CTkLabel(parent, text="New course name",
                            font=("Helvetica Neue", 12),
                            text_color=COLORS["text_muted"])
    new_entry = ctk.CTkEntry(parent, width=340, height=36,
                              font=("Helvetica Neue", 13))

    def on_change(choice):
        if choice == "+ Add new course":
            new_lbl.grid(row=grid_row + 2, column=0, sticky="w", pady=(14, 2))
            new_entry.grid(row=grid_row + 3, column=0, sticky="w")
        else:
            new_lbl.grid_remove()
            new_entry.grid_remove()

    dropdown.configure(command=on_change)
    return var, new_entry, courses


def _resolve_course(var, new_entry, courses):
    selected = var.get()
    if selected == "+ Add new course":
        name = new_entry.get().strip()
        if name:
            add_course(name)
        return get_courses()[-1][0]
    return next(c[0] for c in get_courses() if c[1] == selected)


def build_assignments_page(app, main):
    for w in main.winfo_children():
        w.destroy()

    dark = ctk.get_appearance_mode() == "Dark"
    search_var = ctk.StringVar()

    # ── Layout ────────────────────────────────────────────────────────────────

    # Top bar: title + search
    topbar = ctk.CTkFrame(main, fg_color="transparent", height=72)
    topbar.pack(fill="x", padx=32, pady=(28, 0))
    topbar.pack_propagate(False)

    ctk.CTkLabel(topbar, text="Assignments",
                 font=("Helvetica Neue", 26, "bold")).pack(side="left", anchor="s", pady=8)

    search_entry = ctk.CTkEntry(
        topbar, textvariable=search_var, width=220, height=36,
        placeholder_text="Search assignments...",
        placeholder_text_color="#6A6A85" if dark else "#9090A8",
        fg_color="#1E1E2E" if dark else "#E8E8F4",
        border_color="#34344E" if dark else "#C0C0D8",
        border_width=1,
        font=("Helvetica Neue", 13),
    )
    search_entry.pack(side="right", anchor="s", pady=8)

    # Toolbar
    toolbar = ctk.CTkFrame(main, fg_color="transparent", height=44)
    toolbar.pack(fill="x", padx=32, pady=(10, 0))
    toolbar.pack_propagate(False)

    btn_add = ctk.CTkButton(
        toolbar, text="+ Add", height=34, width=100,
        font=("Helvetica Neue", 13), corner_radius=7,
    )
    btn_add.pack(side="left", padx=(0, 6))

    btn_edit = ctk.CTkButton(
        toolbar, text="Edit", height=34, width=80,
        font=("Helvetica Neue", 13), corner_radius=7,
    )
    btn_edit.pack(side="left", padx=(0, 6))

    btn_delete = ctk.CTkButton(
        toolbar, text="Delete", height=34, width=80,
        font=("Helvetica Neue", 13), corner_radius=7,
        fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
    )
    btn_delete.pack(side="left")

    # Table container
    _apply_table_style()

    table_wrap = ctk.CTkFrame(main, corner_radius=10)  # fg_color from CTk theme
    table_wrap.pack(fill="both", expand=True, padx=32, pady=20)

    table = ttk.Treeview(
        table_wrap,
        style="SP.Treeview",
        columns=("title", "course", "due", "priority", "done"),
        show="headings",
    )
    table.heading("title",    text="Title")
    table.heading("course",   text="Course")
    table.heading("due",      text="Due Date")
    table.heading("priority", text="Priority")
    table.heading("done",     text="Done")

    table.column("title",    width=280, minwidth=180, stretch=True)
    table.column("course",   width=160, minwidth=120, stretch=False)
    table.column("due",      width=100, minwidth=80,  stretch=False, anchor="center")
    table.column("priority", width=70,  minwidth=60,  stretch=False, anchor="center")
    table.column("done",     width=60,  minwidth=50,  stretch=False, anchor="center")

    if dark:
        table.tag_configure("overdue", background="#201318", foreground="#E08888")
        table.tag_configure("soon",    background="#1C1910", foreground="#D4A855")
        table.tag_configure("done",    foreground="#747490")
    else:
        table.tag_configure("overdue", background="#FDE8E8", foreground="#B03030")
        table.tag_configure("soon",    background="#FDF3DC", foreground="#8A6010")
        table.tag_configure("done",    foreground="#9090A8")

    table.pack(fill="both", expand=True)

    # ── Data ──────────────────────────────────────────────────────────────────

    def load_table():
        table.delete(*table.get_children())
        query = search_var.get().lower().strip()

        for row in get_assignments():
            _id, title, course, due, priority, done = row
            if query and query not in f"{title} {course}".lower():
                continue

            due_display = ""
            tag = "done" if done else ""

            if due:
                try:
                    d = datetime.strptime(due, "%Y-%m-%d")
                    due_display = d.strftime("%d/%m/%y")
                    if not done:
                        diff = (d.date() - datetime.today().date()).days
                        if diff < 0:
                            tag = "overdue"
                        elif diff <= 3:
                            tag = "soon"
                except Exception:
                    due_display = due

            table.insert("", "end", iid=_id,
                         values=(title, course or "—", due_display, priority, "✓" if done else ""),
                         tags=(tag,))

    # ── Handlers ──────────────────────────────────────────────────────────────

    def on_double_click(event):
        sel = table.focus()
        if sel:
            toggle_completed(int(sel))
            load_table()

    def on_delete():
        sel = table.focus()
        if not sel:
            return
        if messagebox.askyesno("Delete", "Remove this assignment?"):
            delete_assignment(int(sel))
            load_table()

    def open_add():
        p, form = _popup(app, "New Assignment", height=520)
        e_title = _field(form, "Title", 0, placeholder="e.g. Lab report")
        course_var, new_course_entry, courses = _course_dropdown(form, form, 2)
        e_due = _field(form, "Due date  (DD/MM/YY)", 6, placeholder="e.g. 20/06/26")
        e_pri  = _field(form, "Priority  (1 – 5)", 8, placeholder="3")

        def save():
            title = e_title.get().strip()
            if not title:
                return
            due_input = e_due.get().strip()
            due_db = ""
            if due_input:
                try:
                    due_db = datetime.strptime(due_input, "%d/%m/%y").strftime("%Y-%m-%d")
                except Exception:
                    due_db = due_input
            pri = int(e_pri.get().strip() or "3")
            cid = _resolve_course(course_var, new_course_entry, courses)
            add_assignment(title, cid, due_db, pri)
            p.destroy()
            load_table()

        _popup_buttons(p, p.destroy, save, confirm_label="Add Assignment")

    def open_edit():
        sel = table.focus()
        if not sel:
            return
        r = next(r for r in get_assignments() if r[0] == int(sel))
        _, title, course, due, priority, _ = r

        p, form = _popup(app, "Edit Assignment", height=520)
        e_title = _field(form, "Title", 0, default=title)
        course_var, new_course_entry, courses = _course_dropdown(form, form, 2)
        # set dropdown to current course
        if course:
            course_var.set(course)
        due_default = datetime.strptime(due, "%Y-%m-%d").strftime("%d/%m/%y") if due else ""
        e_due = _field(form, "Due date  (DD/MM/YY)", 6, default=due_default)
        e_pri  = _field(form, "Priority  (1 – 5)", 8, default=str(priority))

        def save():
            due_input = e_due.get().strip()
            due_db = ""
            if due_input:
                try:
                    due_db = datetime.strptime(due_input, "%d/%m/%y").strftime("%Y-%m-%d")
                except Exception:
                    due_db = due_input
            cid = _resolve_course(course_var, new_course_entry, courses)
            update_assignment(int(sel), e_title.get().strip(), cid, due_db,
                              int(e_pri.get().strip() or "3"))
            p.destroy()
            load_table()

        _popup_buttons(p, p.destroy, save, confirm_label="Save Changes")

    # ── Wire up ───────────────────────────────────────────────────────────────

    search_entry.bind("<KeyRelease>", lambda e: load_table())
    table.bind("<Double-1>", on_double_click)
    btn_add.configure(command=open_add)
    btn_edit.configure(command=open_edit)
    btn_delete.configure(command=on_delete)

    load_table()


def _popup_buttons(parent, cancel_cmd, confirm_cmd, confirm_label="Save"):
    bar = ctk.CTkFrame(parent, fg_color="transparent")
    bar.pack(side="bottom", fill="x", padx=28, pady=20)

    ctk.CTkButton(
        bar, text="Cancel", width=110, height=36,
        fg_color="transparent", border_width=1,
        border_color=COLORS["border"],
        font=("Helvetica Neue", 13),
        command=cancel_cmd,
    ).pack(side="left")

    ctk.CTkButton(
        bar, text=confirm_label, width=150, height=36,
        font=("Helvetica Neue", 13),
        command=confirm_cmd,
    ).pack(side="right")
