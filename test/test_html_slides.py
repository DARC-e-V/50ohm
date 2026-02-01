import json
import random

import pytest
from jinja2 import Environment, FileSystemLoader
from mistletoe import Document

import src.config as config
import src.download as download
from renderer.fifty_ohm_html_slide_renderer import FiftyOhmHtmlSlideRenderer

conf = config.Config()
dl = download.Download(conf)
dl.download_git_content()


def parse_katalog():
    with open("data/git_content/contents/questions/fragenkatalog3b.json") as fragenkatalog_file:
        fragenkatalog = json.load(fragenkatalog_file)

        questions = {}

        for exampart in fragenkatalog["sections"]:
            for chapter in exampart["sections"]:
                if "questions" in chapter:
                    for question in chapter["questions"]:
                        questions[question["number"]] = question
                if "sections" in chapter:
                    for section in chapter["sections"]:
                        for question in section["questions"]:
                            questions[question["number"]] = question

        return questions


def filter_shuffle_answers(seq):
    try:
        answers = []
        firstrun = True
        for answer in seq:
            if firstrun:
                answers.append({"content": answer, "correct": True})
                firstrun = False
            else:
                answers.append({"content": answer, "correct": False})
        random.shuffle(answers)
        return answers
    except Exception:
        return seq


def question_stub(number):
    """Combines the original question dataset from BNetzA with our internal metadata"""
    with open("data/git_content/contents/questions/metadata3b.json") as metadata_file:
        metadata = json.load(metadata_file)
        question = questions[number]
        metadata = metadata[f"{number}"]

        if "answer_a" in question:
            answers = [question["answer_a"], question["answer_b"], question["answer_c"], question["answer_d"]]
        else:
            answers = []

        if metadata["picture_a"] != "":
            answer_pictures = [
                metadata["picture_a"],
                metadata["picture_b"],
                metadata["picture_c"],
                metadata["picture_d"],
            ]
        else:
            answer_pictures = []

        if "picture_question" in question:
            picture_question = metadata["picture_question"]
        else:
            picture_question = ""

        return question_template.render(
            question=question["question"],
            number=number,
            layout=metadata["layout"],
            picture_question=picture_question,
            answers=answers,
            answer_pictures=answer_pictures,
        )


env = Environment(loader=FileSystemLoader("templates/"))
env.filters["shuffle_answers"] = filter_shuffle_answers
question_template = env.get_template("slide/question.html")
slide_template = env.get_template("slide/slide.html")
questions = parse_katalog()


@pytest.mark.skip("Requires special files")
@pytest.mark.slide
def test_html_slides(capsys):
    with capsys.disabled():
        with open("test/acceptanceTestSlides.md") as file:
            content = file.read()
            with FiftyOhmHtmlSlideRenderer(question_renderer=question_stub) as renderer:
                output = renderer.render(Document(content))
                with open("test/acceptanceTestSlides.html", "w") as output_file:
                    output_file.write(output)
