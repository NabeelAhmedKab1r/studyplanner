import customtkinter as ctk

from db import init_db

# new UI modules
from ui_assignments import build_assignments_page
from ui_courses import build_courses_page


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Study Planner")
app.geometry("1150x680")


# ---------- SIDEBAR ----------
sidebar = ctk.CTkFrame(app, width=220, corner_radius=15)
sidebar.pack(side="left", fill="y", padx=15, pady=15)

ctk.CTkLabel(
    sidebar,
    text="Study Planner",
    font=("Arial", 26, "bold")
).pack(pady=20)


# ---------- MAIN CONTENT AREA ----------
main = ctk.CTkFrame(app, corner_radius=15)
main.pack(side="left", fill="both", expand=True, padx=15, pady=15)


# ---------- SIDEBAR BUTTONS ----------
ctk.CTkButton(
    sidebar,
    text="Assignments Page",
    command=lambda: build_assignments_page(app, main),
    width=180
).pack(pady=10)

ctk.CTkButton(
    sidebar,
    text="Courses Page",
    command=lambda: build_courses_page(app, main),
    width=180
).pack(pady=10)


# ---------- STARTUP ----------
init_db()

# default page
build_assignments_page(app, main)

app.mainloop()
