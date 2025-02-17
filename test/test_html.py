import json

from jinja2 import Environment, FileSystemLoader
from mistletoe import Document

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer


def parse_katalog():
    with open('data/fragenkatalog3b.json') as fragenkatalog_file:
        fragenkatalog = json.load(fragenkatalog_file)

        questions = {}

        for exampart in fragenkatalog["sections"] : 
            for chapter in exampart["sections"] :
                if "questions" in chapter :
                    for question in chapter["questions"] :
                        questions[question["number"]] = question
                if "sections" in chapter :
                    for section in chapter["sections"] :
                        for question in section["questions"] :
                            questions[question["number"]] = question
        
        return questions

env = Environment(loader=FileSystemLoader('templates/html'))
question_template = env.get_template('question.html')
questions = parse_katalog()

def question_stub(input):
    """ Combines the original question dataset from BNetzA with our internal metadata """
    with open('data/metadata.json') as metadata_file :
        metadata = json.load(metadata_file)
        number = metadata[f"{input}"]["number"] # Fragennummer z.B. AB123

        question = questions[number]
        metadata = metadata[f"{input}"]

        data = {}

        if "answer_a" in question :
            data["answers"] = [
                    question["answer_a"],
                    question["answer_b"],
                    question["answer_c"],
                    question["answer_d"]
                ]
        else :
            data["answers"] = []

        if metadata["picture_a"] != "" :
            data["answer_pictures"] = [
                    metadata["picture_a"],
                    metadata["picture_b"],
                    metadata["picture_c"],
                    metadata["picture_d"]
                ]
        else :
            data["answer_pictures"] = []

        if "picture_question" in question :
            data["picture_question"] = metadata["picture_question"]

        data["question"] = question["question"]
        data["number"] = number

        return question_template.render(data) #fragenkatalog[metadata[f"{input}"]["number"]]


    #metadata[f"{input}"].get("number")


def test_html(capsys):
    with capsys.disabled():
        with open("test/acceptanceTest.md") as file:
            content = file.read()
            with FiftyOhmHtmlRenderer(question_stub) as renderer:
                output = renderer.render(Document(content))
                with open("test/acceptanceTest.html", "w") as output_file:
                    output_file.write(output)
