import json
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class QuestionData:
    number: str
    text: str
    layout: str
    has_solution: bool
    answers: list[str]
    picture_question: str
    answer_pictures: list[str]

    @classmethod
    def not_found(cls, number) -> "QuestionData":
        return cls(
            number="F404",
            text=f"Frage {number} nicht gefunden",
            layout="not-found",
            has_solution=False,
            answers=[],
            picture_question="",
            answer_pictures=[],
        )


class QuestionCatalog(Mapping):
    def __init__(self, questions: dict[str, QuestionData], pool_numbers: set[str], metadata_numbers: set[str]):
        self._questions = questions
        self._pool_numbers = pool_numbers
        self._metadata_numbers = metadata_numbers

    def __getitem__(self, number) -> QuestionData:
        return self._questions[number]

    def __iter__(self) -> Iterator[str]:
        return iter(self._questions)

    def __len__(self) -> int:
        return len(self._questions)

    def missing_note(self, number) -> str:
        return (" (Question not in question pool)" if number not in self._pool_numbers else "") + (
            " (Question not in metadata)" if number not in self._metadata_numbers else ""
        )


def _iter_pool_questions(pool: dict):
    for exampart in pool["sections"]:
        for chapter in exampart["sections"]:
            yield from chapter.get("questions", [])
            for section in chapter.get("sections", []):
                yield from section["questions"]


def _build_question(question: dict, meta: dict, solution_numbers: frozenset[str]) -> QuestionData:
    if "answer_a" in question:
        answers = [question["answer_a"], question["answer_b"], question["answer_c"], question["answer_d"]]
    else:
        answers = []

    if meta["picture_a"] != "":
        answer_pictures = [meta["picture_a"], meta["picture_b"], meta["picture_c"], meta["picture_d"]]
    else:
        answer_pictures = []

    if "picture_question" in question and meta["picture_question"] != "":
        picture_question = meta["picture_question"]
    else:
        picture_question = ""

    number = question["number"]
    return QuestionData(
        number=number,
        text=question["question"],
        layout=meta["layout"],
        has_solution=number in solution_numbers,
        answers=answers,
        picture_question=picture_question,
        answer_pictures=answer_pictures,
    )


def parse_questions(pool_path: Path, metadata_path: Path, solutions_path: Path) -> QuestionCatalog:
    pool = json.loads(pool_path.read_text(encoding="utf-8"))
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    solution_numbers = frozenset(path.stem for path in solutions_path.glob("*.md"))

    pool_questions = {question["number"]: question for question in _iter_pool_questions(pool)}
    questions = {
        number: _build_question(question, metadata[number], solution_numbers)
        for number, question in pool_questions.items()
        if number in metadata
    }

    return QuestionCatalog(questions, set(pool_questions), set(metadata))
