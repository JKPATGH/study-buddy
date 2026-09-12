"""Tkinter GUI for study-buddy: pick a file, take a quiz, see your score."""
import tkinter as tk
from tkinter import filedialog, messagebox

from study_buddy.extractor import extract_text
from study_buddy.quiz_generator import generate_quiz

APP_TITLE = "Study Buddy"


class StudyBuddyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("560x420")
        self.minsize(480, 360)

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
        tk.Label(self, text=APP_TITLE, font=("Helvetica", 22, "bold")).pack(pady=(40, 10))
        tk.Label(
            self,
            text="Upload a PDF, image, or text file to generate a quiz.",
            font=("Helvetica", 13),
            wraplength=440,
        ).pack(pady=(0, 30))

        tk.Button(
            self, text="Choose File...", font=("Helvetica", 13), command=self._choose_file, width=20
        ).pack(pady=10)

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

        tk.Label(
            self, text=f"Question {self.current_index + 1} of {len(self.questions)}",
            font=("Helvetica", 12, "bold"),
        ).pack(pady=(24, 4))

        tk.Label(self, text=q.prompt, font=("Helvetica", 14), wraplength=480, justify="left").pack(pady=(0, 20), padx=20)

        self.selected_choice.set("")
        for choice in q.choices:
            tk.Radiobutton(
                self, text=choice, variable=self.selected_choice, value=choice, font=("Helvetica", 13)
            ).pack(anchor="w", padx=60, pady=4)

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
        tk.Label(
            self, text=f"Score: {self.score}/{len(self.questions)}", font=("Helvetica", 16)
        ).pack(pady=(0, 30))
        tk.Button(
            self, text="Try Another File", font=("Helvetica", 13), command=self._build_start_screen, width=20
        ).pack()


def main():
    app = StudyBuddyApp()
    app.mainloop()


if __name__ == "__main__":
    main()
