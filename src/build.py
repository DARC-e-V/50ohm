import json

from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from joblib import Memory
from mistletoe import Document
from tqdm import tqdm

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer


class Build:
    def __init__(self):
        memory = Memory("./cache", verbose=0)
        self.env = Environment(loader=FileSystemLoader("templates/html"))
        self.questions = self.__parse_katalog()

        # Decorate the method with memory.cache
        self.__build_question = memory.cache(self.__build_question)
        self.__build_chapter  = memory.cache(self.__build_chapter)
        self.__build_section  = memory.cache(self.__build_section)

    def __parse_katalog(self):
        with open("data/fragenkatalog3b.json") as fragenkatalog_file:
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

    # cached
    def __build_question(self, input):
        """Combines the original question dataset from BNetzA with our internal metadata"""

        question_template = self.env.get_template("question.html")

        with open("data/metadata.json") as metadata_file:
            metadata = json.load(metadata_file)
            number = metadata[f"{input}"]["number"]  # Fragennummer z.B. AB123

            question = self.questions[number]
            metadata = metadata[f"{input}"]

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

    # cached
    def __build_chapter(self, edition, number, chapter):
        chapter_template = self.env.get_template("chapter.html")
        with open(f'build/{edition}_chapter_{chapter["ident"]}.html', 'w') as file:
            result = chapter_template.render(
                edition=edition,
                number=number,
                chapter=chapter,
            )
            file.write(result)

    # cached
    def __build_section(self, edition, section, chapter):
        section_template = self.env.get_template("section.html")
        with open(f'build/{edition}_{section["ident"]}.html', 'w') as file:

            with FiftyOhmHtmlRenderer(self.__build_question) as renderer:
                section["content"] = renderer.render(Document(section["content"]))

                result = section_template.render(
                    edition=edition,
                    section=section,
                    chapter=chapter,
                )
                result = BeautifulSoup(result, "html.parser").prettify()

                file.write(result)

    def build_edition(self, edition):
        edition = edition.upper()

        with open(f'data/book_{edition}.json') as f:
            book = json.load(f)

            for number, chapter in enumerate(tqdm(book, desc=f"Build Edition: {edition}"),1):
                self.__build_chapter(edition, number, chapter)

                for section in chapter["sections"] :
                    self.__build_section(edition, section, chapter)