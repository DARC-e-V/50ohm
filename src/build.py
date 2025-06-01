import json
import os
import random
import shutil

from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from joblib import Memory
from mistletoe import Document
from tqdm import tqdm

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_html_slide_renderer import FiftyOhmHtmlSlideRenderer


class Build:
    def __init__(self):
        memory = Memory("./cache", verbose=0)
        self.env = Environment(loader=FileSystemLoader("templates/"))
        self.env.filters["shuffle_answers"] = self.__filter_shuffle_answers
        self.questions = self.__parse_katalog()

        # Decorate the method with memory.cache
        self.__build_question          = memory.cache(self.__build_question)
        self.__build_question_slide    = memory.cache(self.__build_question_slide)
        self.__build_chapter           = memory.cache(self.__build_chapter)
        self.__build_section           = memory.cache(self.__build_section)
        self.__build_page              = memory.cache(self.__build_page)
        self.__build_chapter_slidedeck = memory.cache(self.__build_chapter_slidedeck)

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
    def __build_question(self, input, template_file="html/question.html"):
        """Combines the original question dataset from BNetzA with our internal metadata"""

        question_template = self.env.get_template(template_file)

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

            if "picture_question" in question:
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
    def __build_page(self, content) :
        page_template = self.env.get_template("html/page.html")
        return page_template.render(content=content)
    
    def __picture_handler(self, id):
        os.makedirs("build/pictures", exist_ok=True)
        src = f"data/pictures/{id}.svg"
        dst = f"build/pictures/{id}.svg"
        shutil.copyfile(src, dst)

    def __photo_handler(self, id):
        os.makedirs("build/photos", exist_ok=True)
        src = f"data/photos/{id}.jpg"
        dst = f"build/photos/{id}.jpg"
        shutil.copyfile(src, dst)

    # cached
    def __build_chapter(self, edition, edition_name, number, chapter, next_chapter=None):
        chapter_template = self.env.get_template("html/chapter.html")
        next_chapter_template = self.env.get_template("html/next_chapter.html")
        with open(f'build/{edition}_chapter_{chapter["ident"]}.html', 'w') as file:
            result = chapter_template.render(
                edition=edition,
                name=edition_name,
                number=number,
                chapter=chapter,
            )

            if next_chapter is not None:
                result += next_chapter_template.render(
                    url=f"{edition}_chapter_{next_chapter["ident"]}.html",
                    title=next_chapter["title"],
                )

            result = self.__build_page(result)
            result = BeautifulSoup(result, "html.parser").prettify()
            file.write(result)

    # cached
    def __build_section(self, edition, edition_name, section, section_id, chapter, next_section=None, next_chapter=None):
        section_template = self.env.get_template("html/section.html")
        next_section_template = self.env.get_template("html/next_section.html")
        next_chapter_template = self.env.get_template("html/next_chapter.html")
        with open(f'build/{edition}_{section["ident"]}.html', 'w') as file:

            with FiftyOhmHtmlRenderer(
                question_renderer=self.__build_question,
                picture_handler=self.__picture_handler,
                photo_handler=self.__photo_handler
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
                        url=f"{edition}_{next_section["ident"]}.html",
                        title=next_section["title"],
                    )
                elif next_chapter is not None:
                    result += next_chapter_template.render(
                        url=f"{edition}_chapter_{next_chapter["ident"]}.html",
                        title=next_chapter["title"],
                    )

                result = self.__build_page(result)
                result = BeautifulSoup(result, "html.parser").prettify()
                file.write(result)

    def __build_chapter_slidedeck(self, edition, chapter, sections, next_chapter):
        with open(f'build/{edition}_slide_{chapter["ident"]}.html', 'w') as file:
            slide_template = self.env.get_template("slide/slide.html")
            help_template = self.env.get_template("slide/help.html")
            next_template = self.env.get_template("slide/next.html")
            with FiftyOhmHtmlSlideRenderer(
                question_renderer=self.__build_question_slide,
                picture_handler=self.__picture_handler,
                photo_handler=self.__photo_handler
            ) as renderer:
                result = "<section>\n"
                result += f'<section data-background="#DAEEFA">\n<h1>{chapter["title"]}</h1>\n</section>\n'
                result += help_template.render()
                result += "</section>\n"
                for section in sections:
                    tmp = f'<section data-background="#DAEEFA">\n<h1>{section["title"]}</h1>\n</section>\n'
                    tmp += renderer.render_wrapper(section["slide"])
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
        with open(f"build/{book['edition']}_course_index.html", "w") as file:
            result = template.render(
                book=book,
            )
            result = self.__build_page(result)
            result = BeautifulSoup(result, "html.parser").prettify()
            file.write(result) 
    
    def __build_slide_index(self, book):
        template = self.env.get_template("slide/slide_index.html")
        with open(f"build/{book['edition']}_slide_index.html", "w") as file:
            result = template.render(
                book=book,
            )
            result = self.__build_page(result)
            result = BeautifulSoup(result, "html.parser").prettify()
            file.write(result) 

    def build_edition(self, edition):
        edition = edition.upper()

        with open(f'data/book_{edition}.json') as f:
            book = json.load(f)
            chapters = book["chapters"]
            edition_name = book["title"]
            self.__build_book_index(book)
            self.__build_slide_index(book)
            for number, chapter in enumerate(tqdm(chapters, desc=f"Build Edition: {edition}"),1):
                next_chapter = chapters[number] if number < len(chapters) else None
                self.__build_chapter(edition, edition_name, number, chapter, next_chapter)
                self.__build_chapter_slidedeck(edition, chapter, chapter["sections"], next_chapter)

                for i, section in enumerate(chapter["sections"],1) :
                    next_section = chapter["sections"][i] if i < len(chapter["sections"]) else None
                    self.__build_section(edition, edition_name, section, i, chapter, next_section, next_chapter)

    def build_assets(self):
        shutil.copytree("assets", "build/assets", dirs_exist_ok=True)