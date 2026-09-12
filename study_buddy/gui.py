"""Tkinter desktop app: Study Buddy.

Tabs: Quiz, Calendar, Class Periods, GPA Calculator, High School/College Planner.
All data (calendar, periods, grades, plan) is saved locally to a JSON file so it
persists between launches.
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from study_buddy.extractor import extract_text
from study_buddy.gpa import WEIGHT_BONUS, class_gpa, overall_gpa
from study_buddy.quiz_generator import generate_quiz
from study_buddy.storage import load_data, save_data
from study_buddy.theme import (
    ACCENT,
    BG,
    BORDER,
    CARD_BG,
    FONT_BODY,
    FONT_HEADING,
    FONT_SUBTITLE,
    FONT_TITLE,
    MUTED,
    TEXT,
    apply_theme,
    style_treeview_stripes,
)

APP_TITLE = "Study Buddy"


class StudyBuddyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("760x600")
        self.minsize(660, 500)

        apply_theme(self)
        self.data = load_data()

        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=24, pady=(20, 8))
        tk.Label(header, text="🎓 Study Buddy", font=FONT_TITLE, bg=BG, fg=TEXT).pack(anchor="w")
        tk.Label(
            header, text="Quiz yourself, track your schedule, and plan your future.",
            font=FONT_SUBTITLE, bg=BG, fg=MUTED,
        ).pack(anchor="w", pady=(2, 0))

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=16, pady=(4, 16))

        self.quiz_tab = QuizTab(notebook)
        self.calendar_tab = CalendarTab(notebook, self.data, self._save)
        self.periods_tab = PeriodsTab(notebook, self.data, self._save)
        self.gpa_tab = GpaTab(notebook, self.data, self._save)
        self.planner_tab = PlannerTab(notebook, self.data, self._save)

        notebook.add(self.quiz_tab, text="🧠  Quiz")
        notebook.add(self.calendar_tab, text="📅  Calendar")
        notebook.add(self.periods_tab, text="🕒  Class Periods")
        notebook.add(self.gpa_tab, text="📊  GPA Calculator")
        notebook.add(self.planner_tab, text="🗺️  Planner")

    def _save(self):
        save_data(self.data)


class QuizTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="TFrame")
        self.questions = []
        self.current_index = 0
        self.score = 0
        self.selected_choice = tk.StringVar()
        self._build_start_screen()

    def _clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def _build_start_screen(self):
        self._clear()
        wrapper = tk.Frame(self, bg=BG)
        wrapper.pack(expand=True)
        tk.Label(wrapper, text="📄", font=("Helvetica", 40), bg=BG).pack(pady=(40, 10))
        tk.Label(wrapper, text="Quiz Yourself", font=FONT_TITLE, bg=BG, fg=TEXT).pack()
        tk.Label(
            wrapper, text="Upload a PDF, image, or text file to generate a quiz.",
            font=FONT_SUBTITLE, bg=BG, fg=MUTED, wraplength=440,
        ).pack(pady=(6, 24))
        ttk.Button(wrapper, text="Choose File...", style="Accent.TButton", command=self._choose_file).pack()

    def _choose_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[
                ("Supported files", "*.pdf *.png *.jpg *.jpeg *.bmp *.tiff *.gif *.txt"),
                ("All files", "*.*"),
            ],
        )
        if not file_path:
            return
        try:
            text = extract_text(file_path)
        except Exception as exc:
            messagebox.showerror(APP_TITLE, f"Couldn't read that file:\n{exc}")
            return
        if not text.strip():
            messagebox.showwarning(APP_TITLE, "No readable text was found in that file.")
            return
        self.questions = generate_quiz(text, num_questions=5)
        if not self.questions:
            messagebox.showwarning(APP_TITLE, "Couldn't generate quiz questions from this text.")
            return
        self.current_index = 0
        self.score = 0
        self._build_question_screen()

    def _build_question_screen(self):
        self._clear()
        q = self.questions[self.current_index]

        card = tk.Frame(self, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="both", expand=True, padx=40, pady=30)

        tk.Label(
            card, text=f"QUESTION {self.current_index + 1} OF {len(self.questions)}",
            font=("Helvetica", 11, "bold"), bg=CARD_BG, fg=ACCENT,
        ).pack(pady=(28, 6), padx=30, anchor="w")
        tk.Label(card, text=q.prompt, font=FONT_HEADING, bg=CARD_BG, fg=TEXT, wraplength=560, justify="left").pack(
            pady=(0, 20), padx=30, anchor="w"
        )

        self.selected_choice.set("")
        for choice in q.choices:
            tk.Radiobutton(
                card, text=choice, variable=self.selected_choice, value=choice, font=FONT_BODY,
                bg=CARD_BG, fg=TEXT, selectcolor=CARD_BG, activebackground=CARD_BG, anchor="w",
            ).pack(anchor="w", padx=50, pady=4, fill="x")

        ttk.Button(card, text="Submit", style="Accent.TButton", command=self._submit_answer).pack(pady=26)

    def _submit_answer(self):
        choice = self.selected_choice.get()
        if not choice:
            messagebox.showinfo(APP_TITLE, "Pick an answer first.")
            return
        q = self.questions[self.current_index]
        if choice.lower() == q.answer.lower():
            self.score += 1
        self.current_index += 1
        if self.current_index < len(self.questions):
            self._build_question_screen()
        else:
            self._build_results_screen()

    def _build_results_screen(self):
        self._clear()
        wrapper = tk.Frame(self, bg=BG)
        wrapper.pack(expand=True)
        tk.Label(wrapper, text="🏁", font=("Helvetica", 40), bg=BG).pack(pady=(50, 10))
        tk.Label(wrapper, text="Quiz Complete!", font=FONT_TITLE, bg=BG, fg=TEXT).pack()
        tk.Label(
            wrapper, text=f"Score: {self.score}/{len(self.questions)}",
            font=("Helvetica", 16, "bold"), bg=BG, fg=ACCENT,
        ).pack(pady=(8, 26))
        ttk.Button(wrapper, text="Try Another File", style="Accent.TButton", command=self._build_start_screen).pack()


class CalendarTab(ttk.Frame):
    def __init__(self, parent, data, save_callback):
        super().__init__(parent, style="TFrame")
        self.data = data
        self.save_callback = save_callback

        form = tk.Frame(self, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
        form.pack(fill="x", padx=16, pady=16)
        inner = tk.Frame(form, bg=CARD_BG)
        inner.pack(fill="x", padx=16, pady=14)

        tk.Label(inner, text="Date (YYYY-MM-DD)", font=("Helvetica", 10, "bold"), bg=CARD_BG, fg=MUTED).grid(row=0, column=0, sticky="w")
        self.date_entry = ttk.Entry(inner, width=16)
        self.date_entry.grid(row=1, column=0, padx=(0, 20), sticky="w")

        tk.Label(inner, text="Event / Deadline", font=("Helvetica", 10, "bold"), bg=CARD_BG, fg=MUTED).grid(row=0, column=1, sticky="w")
        self.title_entry = ttk.Entry(inner, width=36)
        self.title_entry.grid(row=1, column=1, padx=(0, 20), sticky="w")

        ttk.Button(inner, text="Add", style="Accent.TButton", command=self._add_event).grid(row=1, column=2)

        table_wrap = tk.Frame(self, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
        table_wrap.pack(fill="both", expand=True, padx=16)
        self.tree = ttk.Treeview(table_wrap, columns=("date", "title"), show="headings", height=14)
        self.tree.heading("date", text="Date")
        self.tree.heading("title", text="Event / Deadline")
        self.tree.column("date", width=120, anchor="center")
        self.tree.column("title", width=440)
        self.tree.pack(fill="both", expand=True, padx=1, pady=1)
        style_treeview_stripes(self.tree)

        ttk.Button(self, text="Remove Selected", style="Secondary.TButton", command=self._remove_selected).pack(pady=12)

        self._refresh()

    def _add_event(self):
        date = self.date_entry.get().strip()
        title = self.title_entry.get().strip()
        if not date or not title:
            messagebox.showinfo(APP_TITLE, "Enter both a date and an event name.")
            return
        self.data["calendar"].append({"date": date, "title": title})
        self.data["calendar"].sort(key=lambda e: e["date"])
        self.save_callback()
        self.date_entry.delete(0, tk.END)
        self.title_entry.delete(0, tk.END)
        self._refresh()

    def _remove_selected(self):
        for item in self.tree.selection():
            index = self.tree.index(item)
            del self.data["calendar"][index]
        self.save_callback()
        self._refresh()

    def _refresh(self):
        self.tree.delete(*self.tree.get_children())
        for i, event in enumerate(self.data["calendar"]):
            self.tree.insert("", "end", values=(event["date"], event["title"]), tags=("odd" if i % 2 else "even",))


class PeriodsTab(ttk.Frame):
    def __init__(self, parent, data, save_callback):
        super().__init__(parent, style="TFrame")
        self.data = data
        self.save_callback = save_callback

        form = tk.Frame(self, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
        form.pack(fill="x", padx=16, pady=16)
        inner = tk.Frame(form, bg=CARD_BG)
        inner.pack(fill="x", padx=16, pady=14)

        labels = ["Period", "Class", "Teacher", "Time"]
        widths = [8, 20, 16, 14]
        self.entries = []
        for col, (label, width) in enumerate(zip(labels, widths)):
            tk.Label(inner, text=label, font=("Helvetica", 10, "bold"), bg=CARD_BG, fg=MUTED).grid(row=0, column=col, sticky="w", padx=(0, 16))
            entry = ttk.Entry(inner, width=width)
            entry.grid(row=1, column=col, padx=(0, 16), sticky="w")
            self.entries.append(entry)
        self.period_entry, self.class_entry, self.teacher_entry, self.time_entry = self.entries

        ttk.Button(inner, text="Add", style="Accent.TButton", command=self._add_period).grid(row=1, column=4)

        table_wrap = tk.Frame(self, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
        table_wrap.pack(fill="both", expand=True, padx=16)
        self.tree = ttk.Treeview(table_wrap, columns=("period", "class_name", "teacher", "time"), show="headings", height=14)
        for col, label, width in [("period", "Period", 70), ("class_name", "Class", 220), ("teacher", "Teacher", 160), ("time", "Time", 140)]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="center" if col == "period" else "w")
        self.tree.pack(fill="both", expand=True, padx=1, pady=1)
        style_treeview_stripes(self.tree)

        ttk.Button(self, text="Remove Selected", style="Secondary.TButton", command=self._remove_selected).pack(pady=12)

        self._refresh()

    def _add_period(self):
        period = self.period_entry.get().strip()
        class_name = self.class_entry.get().strip()
        if not period or not class_name:
            messagebox.showinfo(APP_TITLE, "Enter at least a period number and a class name.")
            return
        self.data["periods"].append({
            "period": period,
            "class_name": class_name,
            "teacher": self.teacher_entry.get().strip(),
            "time": self.time_entry.get().strip(),
        })
        self.data["periods"].sort(key=lambda p: p["period"])
        self.save_callback()
        for entry in self.entries:
            entry.delete(0, tk.END)
        self._refresh()

    def _remove_selected(self):
        for item in self.tree.selection():
            index = self.tree.index(item)
            del self.data["periods"][index]
        self.save_callback()
        self._refresh()

    def _refresh(self):
        self.tree.delete(*self.tree.get_children())
        for i, p in enumerate(self.data["periods"]):
            self.tree.insert("", "end", values=(p["period"], p["class_name"], p["teacher"], p["time"]), tags=("odd" if i % 2 else "even",))


class GpaTab(ttk.Frame):
    def __init__(self, parent, data, save_callback):
        super().__init__(parent, style="TFrame")
        self.data = data
        self.save_callback = save_callback

        form = tk.Frame(self, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
        form.pack(fill="x", padx=16, pady=16)
        inner = tk.Frame(form, bg=CARD_BG)
        inner.pack(fill="x", padx=16, pady=14)

        tk.Label(inner, text="Class", font=("Helvetica", 10, "bold"), bg=CARD_BG, fg=MUTED).grid(row=0, column=0, sticky="w", padx=(0, 16))
        self.class_entry = ttk.Entry(inner, width=20)
        self.class_entry.grid(row=1, column=0, padx=(0, 16), sticky="w")

        tk.Label(inner, text="Grade %", font=("Helvetica", 10, "bold"), bg=CARD_BG, fg=MUTED).grid(row=0, column=1, sticky="w", padx=(0, 16))
        self.pct_entry = ttk.Entry(inner, width=8)
        self.pct_entry.grid(row=1, column=1, padx=(0, 16), sticky="w")

        tk.Label(inner, text="Weight", font=("Helvetica", 10, "bold"), bg=CARD_BG, fg=MUTED).grid(row=0, column=2, sticky="w", padx=(0, 16))
        self.weight_var = tk.StringVar(value="Regular")
        ttk.Combobox(inner, textvariable=self.weight_var, values=list(WEIGHT_BONUS.keys()), width=10, state="readonly").grid(row=1, column=2, padx=(0, 16), sticky="w")

        ttk.Button(inner, text="Add Class", style="Accent.TButton", command=self._add_class).grid(row=1, column=3)

        table_wrap = tk.Frame(self, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
        table_wrap.pack(fill="both", expand=True, padx=16)
        self.tree = ttk.Treeview(table_wrap, columns=("class_name", "percentage", "weight", "gpa"), show="headings", height=11)
        for col, label, width in [("class_name", "Class", 220), ("percentage", "Grade %", 90), ("weight", "Weight", 100), ("gpa", "GPA Points", 100)]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="center" if col != "class_name" else "w")
        self.tree.pack(fill="both", expand=True, padx=1, pady=1)
        style_treeview_stripes(self.tree)

        ttk.Button(self, text="Remove Selected", style="Secondary.TButton", command=self._remove_selected).pack(pady=(12, 6))

        self.gpa_card = tk.Frame(self, bg=ACCENT)
        self.gpa_card.pack(pady=(4, 16))
        self.gpa_label = tk.Label(self.gpa_card, text="Overall GPA: --", font=("Helvetica", 16, "bold"), bg=ACCENT, fg="white", padx=24, pady=10)
        self.gpa_label.pack()

        self._refresh()

    def _add_class(self):
        class_name = self.class_entry.get().strip()
        pct_text = self.pct_entry.get().strip()
        if not class_name or not pct_text:
            messagebox.showinfo(APP_TITLE, "Enter a class name and a grade percentage.")
            return
        try:
            percentage = float(pct_text)
        except ValueError:
            messagebox.showinfo(APP_TITLE, "Grade % must be a number.")
            return

        self.data["gpa_classes"].append({
            "name": class_name,
            "percentage": percentage,
            "weight": self.weight_var.get(),
        })
        self.save_callback()
        self.class_entry.delete(0, tk.END)
        self.pct_entry.delete(0, tk.END)
        self._refresh()

    def _remove_selected(self):
        for item in self.tree.selection():
            index = self.tree.index(item)
            del self.data["gpa_classes"][index]
        self.save_callback()
        self._refresh()

    def _refresh(self):
        self.tree.delete(*self.tree.get_children())
        for i, c in enumerate(self.data["gpa_classes"]):
            points = class_gpa(c["percentage"], c.get("weight", "Regular"))
            self.tree.insert(
                "", "end", values=(c["name"], c["percentage"], c.get("weight", "Regular"), f"{points:.2f}"),
                tags=("odd" if i % 2 else "even",),
            )
        gpa = overall_gpa(self.data["gpa_classes"])
        self.gpa_label.config(text=f"Overall GPA: {gpa:.2f}" if self.data["gpa_classes"] else "Overall GPA: --")


class PlannerTab(ttk.Frame):
    YEARS = ["Freshman", "Sophomore", "Junior", "Senior", "College Yr 1", "College Yr 2", "College Yr 3", "College Yr 4"]

    def __init__(self, parent, data, save_callback):
        super().__init__(parent, style="TFrame")
        self.data = data
        self.save_callback = save_callback

        form = tk.Frame(self, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
        form.pack(fill="x", padx=16, pady=16)
        inner = tk.Frame(form, bg=CARD_BG)
        inner.pack(fill="x", padx=16, pady=14)

        tk.Label(inner, text="Year", font=("Helvetica", 10, "bold"), bg=CARD_BG, fg=MUTED).grid(row=0, column=0, sticky="w", padx=(0, 16))
        self.year_var = tk.StringVar(value=self.YEARS[0])
        ttk.Combobox(inner, textvariable=self.year_var, values=self.YEARS, width=14, state="readonly").grid(row=1, column=0, padx=(0, 16), sticky="w")

        tk.Label(inner, text="Plan / Goal / Course", font=("Helvetica", 10, "bold"), bg=CARD_BG, fg=MUTED).grid(row=0, column=1, sticky="w", padx=(0, 16))
        self.note_entry = ttk.Entry(inner, width=42)
        self.note_entry.grid(row=1, column=1, padx=(0, 16), sticky="w")

        ttk.Button(inner, text="Add", style="Accent.TButton", command=self._add_note).grid(row=1, column=2)

        table_wrap = tk.Frame(self, bg=CARD_BG, highlightbackground=BORDER, highlightthickness=1)
        table_wrap.pack(fill="both", expand=True, padx=16)
        self.tree = ttk.Treeview(table_wrap, columns=("year", "note"), show="headings", height=14)
        self.tree.heading("year", text="Year")
        self.tree.heading("note", text="Plan / Goal / Course")
        self.tree.column("year", width=120, anchor="center")
        self.tree.column("note", width=460)
        self.tree.pack(fill="both", expand=True, padx=1, pady=1)
        style_treeview_stripes(self.tree)

        ttk.Button(self, text="Remove Selected", style="Secondary.TButton", command=self._remove_selected).pack(pady=12)

        self._refresh()

    def _add_note(self):
        note = self.note_entry.get().strip()
        if not note:
            messagebox.showinfo(APP_TITLE, "Enter a plan, goal, or course.")
            return
        self.data["plan"].append({"year": self.year_var.get(), "note": note})
        self.data["plan"].sort(key=lambda p: self.YEARS.index(p["year"]) if p["year"] in self.YEARS else 99)
        self.save_callback()
        self.note_entry.delete(0, tk.END)
        self._refresh()

    def _remove_selected(self):
        for item in self.tree.selection():
            index = self.tree.index(item)
            del self.data["plan"][index]
        self.save_callback()
        self._refresh()

    def _refresh(self):
        self.tree.delete(*self.tree.get_children())
        for i, p in enumerate(self.data["plan"]):
            self.tree.insert("", "end", values=(p["year"], p["note"]), tags=("odd" if i % 2 else "even",))


def main():
    app = StudyBuddyApp()
    app.mainloop()


if __name__ == "__main__":
    main()
