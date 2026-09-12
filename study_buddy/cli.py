#!/usr/bin/env python3
"""Study Buddy CLI: upload a PDF, image, or text file and get quizzed on it."""
import argparse
import string
import sys

from study_buddy.extractor import extract_text
from study_buddy.quiz_generator import generate_quiz


def run_quiz(file_path: str, num_questions: int) -> None:
    print(f"Reading {file_path} ...")
    text = extract_text(file_path)

    if not text.strip():
        print("Couldn't find any readable text in that file.")
        sys.exit(1)

    questions = generate_quiz(text, num_questions=num_questions)
    if not questions:
        print("Couldn't generate quiz questions from this text (try a longer document).")
        sys.exit(1)

    print(f"\nGenerated {len(questions)} question(s). Let's go!\n")
    score = 0
    letters = string.ascii_uppercase

    for i, q in enumerate(questions, start=1):
        print(f"Q{i}: {q.prompt}")
        for letter, choice in zip(letters, q.choices):
            print(f"   {letter}) {choice}")

        answer_letter = input("Your answer: ").strip().upper()
        try:
            chosen = q.choices[letters.index(answer_letter)]
        except (ValueError, IndexError):
            chosen = None

        if chosen and chosen.lower() == q.answer.lower():
            print("Correct!\n")
            score += 1
        else:
            print(f"Nope, the answer was: {q.answer}\n")

    print(f"Final score: {score}/{len(questions)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a quiz from a PDF, image, or text file.")
    parser.add_argument("file", help="Path to a .pdf, .png/.jpg/.jpeg, or .txt file")
    parser.add_argument("-n", "--num-questions", type=int, default=5, help="Number of quiz questions (default: 5)")
    args = parser.parse_args()

    run_quiz(args.file, args.num_questions)


if __name__ == "__main__":
    main()
