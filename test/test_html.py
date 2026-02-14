import json

import pytest
from jinja2 import Environment, FileSystemLoader
from mistletoe import Document

import src.config as config
from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer

conf = config.Config()


def parse_katalog():
    with open(conf.p_data_fragenkatalog) as fragenkatalog_file:
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


env = Environment(loader=FileSystemLoader("templates/html"))
question_template = env.get_template("question.html")


def question_stub(number):
    questions = parse_katalog()
    """Combines the original question dataset from BNetzA with our internal metadata"""
    with open(conf.p_data_metadata) as metadata_file:
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


def include_stub(include):
    with open(conf.p_data_html / f"{include}.html") as file:
        return file.read()


@pytest.mark.skip("Requires special files")
@pytest.mark.html
def test_html(capsys):
    with capsys.disabled():
        with open("test/acceptanceTest.md") as file:
            content = file.read()
            with FiftyOhmHtmlRenderer(
                question_renderer=question_stub,
                include_handler=include_stub,
            ) as renderer:
                output = renderer.render(Document(content))
                with open("test/acceptanceTest.html", "w") as output_file:
                    output_file.write(output)
