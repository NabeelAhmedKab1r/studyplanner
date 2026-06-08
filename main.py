import customtkinter as ctk

from db import init_db
from ui_assignments import build_assignments_page
from ui_courses import build_courses_page

DARK = {
    "bg":         "#0F0F17",
    "sidebar":    "#13131F",
    "border":     "#1E1E2E",
    "nav_hover":  "#1A1A2A",
    "nav_active": "#1E1E30",
    "text":       "#E8E8F0",
    "text_muted": "#5A5A70",
}
LIGHT = {
    "bg":         "#F2F2F8",
    "sidebar":    "#E8E8F2",
    "border":     "#D0D0E0",
    "nav_hover":  "#DCDCEC",
    "nav_active": "#D4D4E8",
    "text":       "#1A1A2E",
    "text_muted": "#707088",
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Study Planner")
app.geometry("1150x700")
app.configure(fg_color=DARK["bg"])

# ---------- SIDEBAR ----------
sidebar = ctk.CTkFrame(app, width=210, corner_radius=0, fg_color=DARK["sidebar"])
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent", height=72)
logo_frame.pack(fill="x")
logo_frame.pack_propagate(False)

logo_label = ctk.CTkLabel(
    logo_frame,
    text="Study Planner",
    font=("Helvetica Neue", 17, "bold"),
    text_color=DARK["text"],
)
logo_label.place(relx=0.5, rely=0.5, anchor="center")

sidebar_divider_top = ctk.CTkFrame(sidebar, height=1, fg_color=DARK["border"])
sidebar_divider_top.pack(fill="x")

nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
nav_frame.pack(fill="x", padx=10, pady=12)

_active_btn = None
_current_page = None

def _set_active(btn):
    global _active_btn
    c = DARK if ctk.get_appearance_mode() == "Dark" else LIGHT
    if _active_btn:
        _active_btn.configure(fg_color="transparent", text_color=c["text_muted"])
    btn.configure(fg_color=c["nav_active"], text_color=c["text"])
    _active_btn = btn

def _nav(parent, label, cmd):
    return ctk.CTkButton(
        parent,
        text=label,
        anchor="w",
        fg_color="transparent",
        hover_color=DARK["nav_hover"],
        text_color=DARK["text_muted"],
        corner_radius=8,
        height=40,
        font=("Helvetica Neue", 13),
        command=cmd,
    )

def _go_assignments():
    global _current_page
    _current_page = build_assignments_page
    _set_active(btn_assignments)
    build_assignments_page(app, main)

def _go_courses():
    global _current_page
    _current_page = build_courses_page
    _set_active(btn_courses)
    build_courses_page(app, main)

btn_assignments = _nav(nav_frame, "  Assignments", _go_assignments)
btn_assignments.pack(fill="x", pady=2)

btn_courses = _nav(nav_frame, "  Courses", _go_courses)
btn_courses.pack(fill="x", pady=2)

# Theme toggle (bottom)
sidebar_divider_bot = ctk.CTkFrame(sidebar, height=1, fg_color=DARK["border"])
sidebar_divider_bot.pack(side="bottom", fill="x")

bottom_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
bottom_frame.pack(side="bottom", fill="x", padx=16, pady=16)

def toggle_theme():
    dark = theme_switch.get() == 1
    mode = "dark" if dark else "light"
    c = DARK if dark else LIGHT
    ctk.set_appearance_mode(mode)

    # Reconfigure sidebar surfaces
    sidebar.configure(fg_color=c["sidebar"])
    main.configure(fg_color=c["bg"])
    sidebar_divider_top.configure(fg_color=c["border"])
    sidebar_divider_bot.configure(fg_color=c["border"])
    logo_label.configure(text_color=c["text"])

    # Recolor nav buttons
    for btn in (btn_assignments, btn_courses):
        btn.configure(hover_color=c["nav_hover"], text_color=c["text_muted"])

    # Restore active state
    if _active_btn:
        _active_btn.configure(fg_color=c["nav_active"], text_color=c["text"])

    # Rebuild current page so treeview style + tags update
    if _current_page:
        _current_page(app, main)

theme_row = ctk.CTkFrame(bottom_frame, fg_color="transparent")
theme_row.pack(fill="x")

ctk.CTkLabel(
    theme_row, text="Dark mode",
    font=("Helvetica Neue", 12),
    text_color=DARK["text_muted"],
).pack(side="left")

theme_switch = ctk.CTkSwitch(theme_row, text="", command=toggle_theme, width=36)
theme_switch.select()
theme_switch.pack(side="right")

# ---------- MAIN CONTENT ----------
main = ctk.CTkFrame(app, corner_radius=0, fg_color=DARK["bg"])
main.pack(side="left", fill="both", expand=True)

# ---------- STARTUP ----------
init_db()
_current_page = build_assignments_page
_set_active(btn_assignments)
build_assignments_page(app, main)

app.mainloop()
