import customtkinter as ctk
from models import get_courses, add_course


def build_courses_page(app, main):
    # clear current page
    for widget in main.winfo_children():
        widget.destroy()

    ctk.CTkLabel(main, text="Courses",
                 font=("Arial", 22, "bold")).pack(pady=15)

    frame = ctk.CTkFrame(main, corner_radius=10)
    frame.pack(fill="both", expand=True, padx=15, pady=10)

    course_listbox = ctk.CTkScrollableFrame(frame, width=600, height=400)
    course_listbox.pack(pady=10)

    def refresh():
        for w in course_listbox.winfo_children():
            w.destroy()

        for cid, name in get_courses():
            row = ctk.CTkFrame(course_listbox)
            row.pack(fill="x", pady=4)

            ctk.CTkLabel(row, text=name,
                         anchor="w").pack(side="left", padx=10)

    refresh()

    def add_course_popup():
        p = ctk.CTkToplevel(app)
        p.title("Add Course")

        entry = ctk.CTkEntry(p)
        entry.pack(pady=10)

        def save():
            add_course(entry.get())
            p.destroy()
            refresh()

        ctk.CTkButton(p, text="Save", command=save).pack(pady=10)

    ctk.CTkButton(
        main,
        text="Add Course",
        command=add_course_popup
    ).pack(pady=10)
