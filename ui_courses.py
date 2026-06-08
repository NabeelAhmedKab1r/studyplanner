import customtkinter as ctk
from models import get_courses, add_course

COLORS = {
    "bg":          "#0F0F17",
    "card":        "#13131F",
    "card_hover":  "#1A1A2A",
    "border":      "#1E1E2E",
    "text":        "#E8E8F0",
    "text_muted":  "#5A5A70",
    "secondary":   "#1E1E2E",
}

PALETTE = [
    "#6366F1", "#8B5CF6", "#EC4899", "#14B8A6",
    "#F59E0B", "#10B981", "#3B82F6", "#EF4444",
]


def build_courses_page(app, main):
    for w in main.winfo_children():
        w.destroy()

    # Header
    header = ctk.CTkFrame(main, fg_color="transparent", height=72)
    header.pack(fill="x", padx=32, pady=(28, 0))
    header.pack_propagate(False)

    ctk.CTkLabel(header, text="Courses",
                 font=("Helvetica Neue", 26, "bold"),
                 text_color=COLORS["text"]).pack(side="left", anchor="s", pady=8)

    btn_add = ctk.CTkButton(
        header, text="+ Add Course", height=34, width=120,
        font=("Helvetica Neue", 13), corner_radius=7,
    )
    btn_add.pack(side="right", anchor="s", pady=8)

    # Scrollable card grid
    scroll = ctk.CTkScrollableFrame(main, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=24, pady=20)

    grid = ctk.CTkFrame(scroll, fg_color="transparent")
    grid.pack(fill="both", expand=True)

    COLS = 3

    def refresh():
        for w in grid.winfo_children():
            w.destroy()

        courses = get_courses()

        if not courses:
            ctk.CTkLabel(
                grid, text="No courses yet.\nClick '+ Add Course' to get started.",
                font=("Helvetica Neue", 15),
                text_color=COLORS["text_muted"],
                justify="center",
            ).pack(pady=80)
            return

        for i, (cid, name) in enumerate(courses):
            color = PALETTE[i % len(PALETTE)]
            _course_card(grid, cid, name, color, i, COLS)

        for c in range(COLS):
            grid.columnconfigure(c, weight=1)

    def add_course_popup():
        p = ctk.CTkToplevel(app)
        p.title("Add Course")
        p.geometry("380x200")
        p.resizable(False, False)
        p.grab_set()

        ctk.CTkLabel(p, text="New Course",
                     font=("Helvetica Neue", 18, "bold")).pack(
            pady=(24, 12), padx=28, anchor="w")

        entry = ctk.CTkEntry(p, width=324, height=36,
                             placeholder_text="e.g. Linear Algebra",
                             font=("Helvetica Neue", 13))
        entry.pack(padx=28)
        entry.focus()

        bar = ctk.CTkFrame(p, fg_color="transparent")
        bar.pack(side="bottom", fill="x", padx=28, pady=20)

        def save():
            name = entry.get().strip()
            if name:
                add_course(name)
                p.destroy()
                refresh()

        entry.bind("<Return>", lambda e: save())

        ctk.CTkButton(bar, text="Cancel", width=110, height=36,
                      fg_color="transparent", border_width=1,
                      border_color=COLORS["border"],
                      font=("Helvetica Neue", 13),
                      command=p.destroy).pack(side="left")

        ctk.CTkButton(bar, text="Add Course", width=130, height=36,
                      font=("Helvetica Neue", 13),
                      command=save).pack(side="right")

    btn_add.configure(command=add_course_popup)
    refresh()


def _course_card(parent, cid, name, color, index, cols):
    card = ctk.CTkFrame(parent, fg_color=COLORS["card"],
                         corner_radius=10, height=100)
    card.grid(row=index // cols, column=index % cols,
               padx=8, pady=8, sticky="nsew")
    card.grid_propagate(False)

    # Left color strip
    strip = ctk.CTkFrame(card, fg_color=color, width=5, corner_radius=0)
    strip.pack(side="left", fill="y")

    content = ctk.CTkFrame(card, fg_color="transparent")
    content.pack(side="left", fill="both", expand=True, padx=16, pady=14)

    ctk.CTkLabel(content, text=name,
                 font=("Helvetica Neue", 14, "bold"),
                 text_color=COLORS["text"],
                 anchor="w", wraplength=170).pack(anchor="w")

    ctk.CTkLabel(content, text=f"Course #{cid}",
                 font=("Helvetica Neue", 11),
                 text_color=COLORS["text_muted"],
                 anchor="w").pack(anchor="w", pady=(4, 0))
