import json
import random
import shutil

from jinja2 import Environment, FileSystemLoader
from joblib import Memory
from mistletoe import Document
from tqdm import tqdm

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_html_slide_renderer import FiftyOhmHtmlSlideRenderer

from .config import Config


class Build:
    def __init__(self, config: Config):
        self.config = config

        memory = Memory("./cache", verbose=0)
        self.env = Environment(loader=FileSystemLoader("templates/"))
        self.env.filters["shuffle_answers"] = self.__filter_shuffle_answers
        self.questions = self.__parse_katalog()

        # Decorate the method with memory.cache
        self.__build_question = memory.cache(self.__build_question)
        self.__build_question_slide = memory.cache(self.__build_question_slide)
        self.__build_chapter = memory.cache(self.__build_chapter)
        self.__build_section = memory.cache(self.__build_section)
        self.__build_chapter_slidedeck = memory.cache(self.__build_chapter_slidedeck)

    def __parse_katalog(self):
        with self.config.p_fragenkatalog.open() as file:
            fragenkatalog = json.load(file)

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
    def __build_question(self, input, template_file="html/question.html"):
        """Combines the original question dataset from BNetzA with our internal metadata"""

        question_template = self.env.get_template(template_file)

        with (self.config.p_data / "metadata3b.json").open() as file:
            metadata = json.load(file)

            question = None
            number = None
            if f"{input}" in metadata:
                metadata = metadata[f"{input}"]
                number = metadata["number"]  # Fragennummer z.B. AB123
                if number in self.questions:
                    question = self.questions[number]

            if question is None:
                tqdm.write(
                    f"\033[31mQuestion #{input} is missing"
                    + (f" (but found number: {number})" if number is not None else "")
                    + "\033[0m"
                )
                metadata = {"layout": "not-found", "picture_a": ""}
                number = 404
                question = {"question": f"Frage {input} nicht gefunden"}

            if "answer_a" in question:
                answers = [question["answer_a"], question["answer_b"], question["answer_c"], question["answer_d"]]
            else:
                answers = []

            if metadata["picture_a"] != "":
                self.__picture_handler(metadata["picture_a"])
                self.__picture_handler(metadata["picture_b"])
                self.__picture_handler(metadata["picture_c"])
                self.__picture_handler(metadata["picture_d"])

                answer_pictures = [
                    metadata["picture_a"],
                    metadata["picture_b"],
                    metadata["picture_c"],
                    metadata["picture_d"],
                ]
            else:
                answer_pictures = []

            if "picture_question" in question and metadata["picture_question"] != "":
                picture_question = metadata["picture_question"]
                self.__picture_handler(picture_question)
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

    def __build_question_slide(self, input):
        return self.__build_question(input, template_file="slide/question.html")

    # cached
    def __build_page(self, content, course_wrapper=False, sidebar=None):
        page_template = self.env.get_template("html/page.html")
        return page_template.render(content=content, course_wrapper=course_wrapper, sidebar=sidebar)

    def __picture_handler(self, id):
        self.config.p_build_pictures.mkdir(parents=True, exist_ok=True)
        file = f"{id}.svg"
        try:
            shutil.copyfile(self.config.p_data_pictures / file, self.config.p_build_pictures / file)
        except FileNotFoundError:
            tqdm.write(f"\033[31mPicture #{id} not found\033[0m")

    def __photo_handler(self, id):
        self.config.p_build_photos.mkdir(parents=True, exist_ok=True)
        file = f"{id}.jpg"
        try:
            shutil.copyfile(self.config.p_data_photos / file, self.config.p_build_photos / file)
        except FileNotFoundError:
            tqdm.write(f"\033[31mPhoto #{id} not found\033[0m")

    # cached
    def __build_chapter(self, edition, edition_name, number, chapter, next_chapter=None):
        chapter_template = self.env.get_template("html/chapter.html")
        next_chapter_template = self.env.get_template("html/next_chapter.html")
        with (self.config.p_build / f"{edition}_chapter_{chapter['ident']}.html").open("w") as file:
            result = chapter_template.render(
                edition=edition,
                name=edition_name,
                number=number,
                chapter=chapter,
            )

            if next_chapter is not None:
                result += next_chapter_template.render(
                    url=f"{edition}_chapter_{next_chapter['ident']}.html",
                    title=next_chapter["title"],
                )

            result = self.__build_page(result, course_wrapper=True)
            file.write(result)

    def __include_handler(self, include):
        with (self.config.p_data / "includes.json").open() as file:
            includes = json.load(file)
            return includes.get(include)

    # cached
    def __build_section(
        self, edition, edition_name, section, section_id, chapter, next_section=None, next_chapter=None
    ):
        section_template = self.env.get_template("html/section.html")
        next_section_template = self.env.get_template("html/next_section.html")
        next_chapter_template = self.env.get_template("html/next_chapter.html")
        with (self.config.p_build / f"{edition}_{section['ident']}.html").open("w") as file:
            with FiftyOhmHtmlRenderer(
                question_renderer=self.__build_question,
                picture_handler=self.__picture_handler,
                photo_handler=self.__photo_handler,
                include_handler=self.__include_handler,
            ) as renderer:
                section["content"] = renderer.render(Document(section["content"]))

                result = section_template.render(
                    edition=edition,
                    name=edition_name,
                    section=section,
                    section_id=section_id,
                    chapter=chapter,
                )

                if next_section is not None:
                    result += next_section_template.render(
                        url=f"{edition}_{next_section['ident']}.html",
                        title=next_section["title"],
                    )
                elif next_chapter is not None:
                    result += next_chapter_template.render(
                        url=f"{edition}_chapter_{next_chapter['ident']}.html",
                        title=next_chapter["title"],
                    )

                result = self.__build_page(result, course_wrapper=True)
                file.write(result)

    def __build_chapter_slidedeck(self, edition, chapter, sections, next_chapter):
        with (self.config.p_build / f"{edition}_slide_{chapter['ident']}.html").open("w") as file:
            slide_template = self.env.get_template("slide/slide.html")
            help_template = self.env.get_template("slide/help.html")
            next_template = self.env.get_template("slide/next.html")
            with FiftyOhmHtmlSlideRenderer(
                question_renderer=self.__build_question_slide,
                picture_handler=self.__picture_handler,
                photo_handler=self.__photo_handler,
                include_handler=self.__include_handler,
            ) as renderer:
                result = "<section>\n"
                result += f'<section data-background="#DAEEFA">\n<h1>{chapter["title"]}</h1>\n</section>\n'
                result += help_template.render()
                result += "</section>\n"
                for section in sections:
                    if section["slide"] is None:
                        continue

                    if not section["slide"].startswith("---"):
                        section["slide"] = "---\n" + section["slide"]
                    tmp = f'<section data-background="#DAEEFA">\n<h1>{section["title"]}</h1>\n</section>\n'
                    tmp += renderer.render(Document(section["slide"]))
                    result += f"<section>{tmp}</section>\n"
                result += next_template.render(
                    edition=edition,
                    next_chapter=next_chapter,
                    chapter=chapter,
                )

                result = slide_template.render(content=result)
                file.write(result)

    def __filter_shuffle_answers(self, seq):
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

    def __build_book_index(self, book):
        template = self.env.get_template("html/course_index.html")
        with (self.config.p_build / f"{book['edition']}_course_index.html").open("w") as file:
            result = template.render(
                book=book,
            )
            result = self.__build_page(result)
            file.write(result)

    def __build_slide_index(self, book):
        template = self.env.get_template("slide/slide_index.html")
        with (self.config.p_build / f"{book['edition']}_slide_index.html").open("w") as file:
            result = template.render(
                book=book,
            )
            result = self.__build_page(result)
            file.write(result)

    def build_edition(self, edition):
        self.config.p_build.mkdir(exist_ok=True)

        edition = edition.upper()

        with (self.config.p_data / f"book_{edition}.json").open() as file:
            book = json.load(file)
            chapters = book["chapters"]
            edition_name = book["title"]
            self.__build_book_index(book)
            self.__build_slide_index(book)
            for number, chapter in enumerate(tqdm(chapters, desc=f"Build Edition: {edition}"), 1):
                next_chapter = chapters[number] if number < len(chapters) else None
                self.__build_chapter(edition, edition_name, number, chapter, next_chapter)
                self.__build_chapter_slidedeck(edition, chapter, chapter["sections"], next_chapter)

                for i, section in enumerate(chapter["sections"], 1):
                    tqdm.write(f"Rendering section {section['title']}")
                    next_section = chapter["sections"][i] if i < len(chapter["sections"]) else None
                    self.__build_section(edition, edition_name, section, i, chapter, next_section, next_chapter)

    def build_assets(self):
        self.config.p_build.mkdir(exist_ok=True)
        shutil.copytree(self.config.p_assets, self.config.p_build_assets, dirs_exist_ok=True)

    def __parse_snippets(self):
        with (self.config.p_data / "snippets.json").open() as file:
            snippets = json.load(file)

            with FiftyOhmHtmlRenderer(
                question_renderer=self.__build_question,
                picture_handler=self.__picture_handler,
                photo_handler=self.__photo_handler,
                include_handler=self.__include_handler,
            ) as renderer:
                for key, value in snippets.items():
                    snippets[key] = renderer.render_inner(Document(value))
                    # Remove leading <p> and trailing </p>:
                    snippets[key] = snippets[key][3:-4]
        return snippets

    def __parse_contents(self):
        with (self.config.p_data / "content.json").open() as file:
            contents = json.load(file)
            return contents

    def __build_index(self, snippets):
        template = self.env.get_template("html/index.html")
        result = template.render({"snippets": snippets})

        with (self.config.p_build / "index.html").open("w") as file:
            result = self.__build_page(result)

            file.write(result)

    def __build_course_page(self, snippets, template, page):
        template = self.env.get_template(f"html/{template}.html")
        result = template.render({"snippets": snippets})

        with (self.config.p_build / f"{page}.html").open("w") as file:
            result = self.__build_page(result)
            file.write(result)

    def __build_html_page(self, contents, page):
        for content in contents:
            if content["url_part"] == page:
                with (self.config.p_build / f"{page}.html").open("w") as file:
                    result = self.__build_page(content=content["content"], sidebar=content["sidebar"])
                    file.write(result)

    def build_website(self):
        self.config.p_build.mkdir(exist_ok=True)

        snippets = self.__parse_snippets()
        contents = self.__parse_contents()
        self.__build_index(snippets)
        self.__build_course_page(snippets, "kurse-karte", "kurse_vor_ort_karte")
        self.__build_course_page(snippets, "kurse-liste", "kurse_vor_ort_liste")
        self.__build_course_page(snippets, "patenkarte", "patenkarte")
        self.__build_html_page(contents, "pruefung")
        self.__build_html_page(contents, "infos")
