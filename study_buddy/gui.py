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

APP_TITLE = "Study Buddy"


class StudyBuddyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("720x560")
        self.minsize(620, 480)

        self.data = load_data()

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self.quiz_tab = QuizTab(notebook)
        self.calendar_tab = CalendarTab(notebook, self.data, self._save)
        self.periods_tab = PeriodsTab(notebook, self.data, self._save)
        self.gpa_tab = GpaTab(notebook, self.data, self._save)
        self.planner_tab = PlannerTab(notebook, self.data, self._save)

        notebook.add(self.quiz_tab, text="Quiz")
        notebook.add(self.calendar_tab, text="Calendar")
        notebook.add(self.periods_tab, text="Class Periods")
        notebook.add(self.gpa_tab, text="GPA Calculator")
        notebook.add(self.planner_tab, text="Planner")

    def _save(self):
        save_data(self.data)


class QuizTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
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
        tk.Label(self, text="Quiz Yourself", font=("Helvetica", 20, "bold")).pack(pady=(40, 10))
        tk.Label(
            self,
            text="Upload a PDF, image, or text file to generate a quiz.",
            font=("Helvetica", 13),
            wraplength=440,
        ).pack(pady=(0, 30))
        tk.Button(self, text="Choose File...", font=("Helvetica", 13), command=self._choose_file, width=20).pack(pady=10)

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
        tk.Label(self, text=f"Question {self.current_index + 1} of {len(self.questions)}", font=("Helvetica", 12, "bold")).pack(pady=(24, 4))
        tk.Label(self, text=q.prompt, font=("Helvetica", 14), wraplength=560, justify="left").pack(pady=(0, 20), padx=20)
        self.selected_choice.set("")
        for choice in q.choices:
            tk.Radiobutton(self, text=choice, variable=self.selected_choice, value=choice, font=("Helvetica", 13)).pack(anchor="w", padx=60, pady=4)
        tk.Button(self, text="Submit", font=("Helvetica", 13), command=self._submit_answer, width=16).pack(pady=24)

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
        tk.Label(self, text="Quiz Complete!", font=("Helvetica", 22, "bold")).pack(pady=(50, 10))
        tk.Label(self, text=f"Score: {self.score}/{len(self.questions)}", font=("Helvetica", 16)).pack(pady=(0, 30))
        tk.Button(self, text="Try Another File", font=("Helvetica", 13), command=self._build_start_screen, width=20).pack()


class CalendarTab(ttk.Frame):
    def __init__(self, parent, data, save_callback):
        super().__init__(parent)
        self.data = data
        self.save_callback = save_callback

        form = ttk.Frame(self)
        form.pack(fill="x", padx=16, pady=16)

        ttk.Label(form, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w")
        self.date_entry = ttk.Entry(form, width=16)
        self.date_entry.grid(row=0, column=1, padx=(6, 20))

        ttk.Label(form, text="Event / Deadline:").grid(row=0, column=2, sticky="w")
        self.title_entry = ttk.Entry(form, width=32)
        self.title_entry.grid(row=0, column=3, padx=(6, 20))

        ttk.Button(form, text="Add", command=self._add_event).grid(row=0, column=4)

        self.tree = ttk.Treeview(self, columns=("date", "title"), show="headings", height=14)
        self.tree.heading("date", text="Date")
        self.tree.heading("title", text="Event / Deadline")
        self.tree.column("date", width=120, anchor="center")
        self.tree.column("title", width=440)
        self.tree.pack(fill="both", expand=True, padx=16)

        ttk.Button(self, text="Remove Selected", command=self._remove_selected).pack(pady=10)

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
        for event in self.data["calendar"]:
            self.tree.insert("", "end", values=(event["date"], event["title"]))


class PeriodsTab(ttk.Frame):
    def __init__(self, parent, data, save_callback):
        super().__init__(parent)
        self.data = data
        self.save_callback = save_callback

        form = ttk.Frame(self)
        form.pack(fill="x", padx=16, pady=16)

        ttk.Label(form, text="Period:").grid(row=0, column=0, sticky="w")
        self.period_entry = ttk.Entry(form, width=8)
        self.period_entry.grid(row=0, column=1, padx=(6, 20))

        ttk.Label(form, text="Class:").grid(row=0, column=2, sticky="w")
        self.class_entry = ttk.Entry(form, width=20)
        self.class_entry.grid(row=0, column=3, padx=(6, 20))

        ttk.Label(form, text="Teacher:").grid(row=0, column=4, sticky="w")
        self.teacher_entry = ttk.Entry(form, width=16)
        self.teacher_entry.grid(row=0, column=5, padx=(6, 20))

        ttk.Label(form, text="Time:").grid(row=0, column=6, sticky="w")
        self.time_entry = ttk.Entry(form, width=14)
        self.time_entry.grid(row=0, column=7, padx=(6, 20))

        ttk.Button(form, text="Add", command=self._add_period).grid(row=0, column=8)

        self.tree = ttk.Treeview(self, columns=("period", "class_name", "teacher", "time"), show="headings", height=14)
        for col, label, width in [("period", "Period", 70), ("class_name", "Class", 220), ("teacher", "Teacher", 160), ("time", "Time", 140)]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="center" if col == "period" else "w")
        self.tree.pack(fill="both", expand=True, padx=16)

        ttk.Button(self, text="Remove Selected", command=self._remove_selected).pack(pady=10)

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
        for entry in (self.period_entry, self.class_entry, self.teacher_entry, self.time_entry):
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
        for p in self.data["periods"]:
            self.tree.insert("", "end", values=(p["period"], p["class_name"], p["teacher"], p["time"]))


class GpaTab(ttk.Frame):
    def __init__(self, parent, data, save_callback):
        super().__init__(parent)
        self.data = data
        self.save_callback = save_callback

        form = ttk.Frame(self)
        form.pack(fill="x", padx=16, pady=16)

        ttk.Label(form, text="Class:").grid(row=0, column=0, sticky="w")
        self.class_entry = ttk.Entry(form, width=20)
        self.class_entry.grid(row=0, column=1, padx=(6, 20))

        ttk.Label(form, text="Grade %:").grid(row=0, column=2, sticky="w")
        self.pct_entry = ttk.Entry(form, width=8)
        self.pct_entry.grid(row=0, column=3, padx=(6, 20))

        ttk.Label(form, text="Weight:").grid(row=0, column=4, sticky="w")
        self.weight_var = tk.StringVar(value="Regular")
        ttk.Combobox(form, textvariable=self.weight_var, values=list(WEIGHT_BONUS.keys()), width=10, state="readonly").grid(row=0, column=5, padx=(6, 20))

        ttk.Button(form, text="Add Class", command=self._add_class).grid(row=0, column=6)

        self.tree = ttk.Treeview(self, columns=("class_name", "percentage", "weight", "gpa"), show="headings", height=12)
        for col, label, width in [("class_name", "Class", 220), ("percentage", "Grade %", 90), ("weight", "Weight", 100), ("gpa", "GPA Points", 100)]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="center" if col != "class_name" else "w")
        self.tree.pack(fill="both", expand=True, padx=16)

        ttk.Button(self, text="Remove Selected", command=self._remove_selected).pack(pady=(10, 4))

        self.gpa_label = tk.Label(self, text="Overall GPA: --", font=("Helvetica", 16, "bold"))
        self.gpa_label.pack(pady=(4, 16))

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
        for c in self.data["gpa_classes"]:
            points = class_gpa(c["percentage"], c.get("weight", "Regular"))
            self.tree.insert("", "end", values=(c["name"], c["percentage"], c.get("weight", "Regular"), f"{points:.2f}"))
        gpa = overall_gpa(self.data["gpa_classes"])
        self.gpa_label.config(text=f"Overall GPA: {gpa:.2f}" if self.data["gpa_classes"] else "Overall GPA: --")


class PlannerTab(ttk.Frame):
    YEARS = ["Freshman", "Sophomore", "Junior", "Senior", "College Yr 1", "College Yr 2", "College Yr 3", "College Yr 4"]

    def __init__(self, parent, data, save_callback):
        super().__init__(parent)
        self.data = data
        self.save_callback = save_callback

        form = ttk.Frame(self)
        form.pack(fill="x", padx=16, pady=16)

        ttk.Label(form, text="Year:").grid(row=0, column=0, sticky="w")
        self.year_var = tk.StringVar(value=self.YEARS[0])
        ttk.Combobox(form, textvariable=self.year_var, values=self.YEARS, width=14, state="readonly").grid(row=0, column=1, padx=(6, 20))

        ttk.Label(form, text="Plan / Goal / Course:").grid(row=0, column=2, sticky="w")
        self.note_entry = ttk.Entry(form, width=40)
        self.note_entry.grid(row=0, column=3, padx=(6, 20))

        ttk.Button(form, text="Add", command=self._add_note).grid(row=0, column=4)

        self.tree = ttk.Treeview(self, columns=("year", "note"), show="headings", height=14)
        self.tree.heading("year", text="Year")
        self.tree.heading("note", text="Plan / Goal / Course")
        self.tree.column("year", width=120, anchor="center")
        self.tree.column("note", width=460)
        self.tree.pack(fill="both", expand=True, padx=16)

        ttk.Button(self, text="Remove Selected", command=self._remove_selected).pack(pady=10)

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
        for p in self.data["plan"]:
            self.tree.insert("", "end", values=(p["year"], p["note"]))


def main():
    app = StudyBuddyApp()
    app.mainloop()


if __name__ == "__main__":
    main()
