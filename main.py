import customtkinter as ctk
from tkinter import ttk

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

# Set column widths
table.column("title", width=260)
table.column("course", width=180)
table.column("due", width=140)
table.column("priority", width=120)

table.pack(fill="both", expand=True, padx=10, pady=10)

app.mainloop()
