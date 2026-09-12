"""Generates multiple-choice fill-in-the-blank quiz questions from plain text (no AI required)."""
import random
import re
from dataclasses import dataclass

STOPWORDS = {
    "the", "and", "for", "are", "but", "not", "you", "all", "can", "her", "was",
    "one", "our", "out", "day", "get", "has", "him", "his", "how", "man", "new",
    "now", "old", "see", "two", "way", "who", "boy", "did", "its", "let", "put",
    "say", "she", "too", "use", "that", "with", "this", "from", "have", "will",
    "your", "they", "been", "were", "into", "than", "them", "then", "when",
    "what", "which", "their", "would", "there", "could", "these", "those",
    "about", "after", "also", "such", "each", "because", "while", "some",
}


@dataclass
class Question:
    prompt: str
    choices: list[str]
    answer: str


def _split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if 6 <= len(s.split()) <= 30]


def _candidate_keyword(sentence: str) -> str | None:
    words = re.findall(r"[A-Za-z]+", sentence)
    candidates = [w for w in words if len(w) >= 5 and w.lower() not in STOPWORDS]
    if not candidates:
        return None
    return max(candidates, key=len)


def generate_quiz(text: str, num_questions: int = 5) -> list[Question]:
    """Build multiple-choice questions by blanking out a key word in selected sentences."""
    sentences = _split_sentences(text)
    random.shuffle(sentences)

    keyword_pool: list[str] = []
    prepared: list[tuple[str, str]] = []
    for sentence in sentences:
        keyword = _candidate_keyword(sentence)
        if not keyword:
            continue
        prepared.append((sentence, keyword))
        keyword_pool.append(keyword)
        if len(prepared) >= num_questions * 3:
            break

    questions: list[Question] = []
    used_keywords = set()
    for sentence, keyword in prepared:
        if keyword.lower() in used_keywords:
            continue
        used_keywords.add(keyword.lower())

        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        blanked = pattern.sub("_____", sentence, count=1)

        distractor_pool = [w for w in keyword_pool if w.lower() != keyword.lower()]
        distractors = random.sample(distractor_pool, k=min(3, len(distractor_pool)))

        choices = distractors + [keyword]
        random.shuffle(choices)

        questions.append(Question(prompt=blanked, choices=choices, answer=keyword))
        if len(questions) >= num_questions:
            break

    return questions
