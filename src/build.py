import functools
import json
import random
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from mistletoe import Document
from tqdm import tqdm

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_html_slide_renderer import FiftyOhmHtmlSlideRenderer

from .config import Config


class Build:
    def __init__(self, config: Config):
        self.config = config

        self.env = Environment(loader=FileSystemLoader("templates/"))
        self.env.filters["shuffle_answers"] = self.__filter_shuffle_answers
        self.questions = self.__parse_katalog()

    def __parse_katalog(self):
        with self.config.p_data_fragenkatalog.open() as file:
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

    def __build_question(self, number, template_file="html/question.html"):
        """Combines the original question dataset from BNetzA with our internal metadata"""

        question_template = self.env.get_template(template_file)

        with (self.config.p_data_metadata).open() as file:
            metadata_json = json.load(file)

            question = None
            metadata = None

            if number in self.questions:
                question = self.questions[number]

            if number in metadata_json:
                metadata = metadata_json[number]

            if question is None or metadata is None:
                tqdm.write(
                    f"\033[31mQuestion #{number} is missing"
                    + (" (Question not in question pool)" if question is None else "")
                    + (" (Question not in metadata)" if metadata is None else "")
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
                alt_text_a = self.__picture_handler(metadata["picture_a"])
                alt_text_b = self.__picture_handler(metadata["picture_b"])
                alt_text_c = self.__picture_handler(metadata["picture_c"])
                alt_text_d = self.__picture_handler(metadata["picture_d"])

                answer_pictures = [
                    metadata["picture_a"],
                    metadata["picture_b"],
                    metadata["picture_c"],
                    metadata["picture_d"],
                ]

                alt_text_answers = [
                    alt_text_a,
                    alt_text_b,
                    alt_text_c,
                    alt_text_d,
                ]

            else:
                answer_pictures = []
                alt_text_answers = []

            if "picture_question" in question and metadata["picture_question"] != "":
                picture_question = metadata["picture_question"]
                alt_text_question = self.__picture_handler(picture_question)
            else:
                picture_question = ""
                alt_text_question = ""

            brightspot_file = self.config.p_data_brightspots / f"{number}.md"

            return question_template.render(
                question=question["question"],
                number=number,
                layout=metadata["layout"],
                picture_question=picture_question,
                answers=answers,
                answer_pictures=answer_pictures,
                alt_text_answers=alt_text_answers,
                alt_text_question=alt_text_question,
                brightspot=brightspot_file.exists(),
            )

    def __build_question_slide(self, input):
        return self.__build_question(input, template_file="slide/question.html")

    def __build_page(self, content, course_wrapper=False, sidebar=None):
        page_template = self.env.get_template("html/page.html")
        return page_template.render(content=content, course_wrapper=course_wrapper, sidebar=sidebar)

    def __picture_handler(self, id):
        self.config.p_build_pictures.mkdir(parents=True, exist_ok=True)
        file = f"{id}.svg"
        try:
            shutil.copyfile(self.config.p_data_pictures / file, self.config.p_build_pictures / file)
            if (self.config.p_data_pictures / f"{id}.txt").exists():
                return (self.config.p_data_pictures / f"{id}.txt").read_text()
            else:
                return "Bildbeschreibung noch nicht verfügbar"
        except FileNotFoundError:
            tqdm.write(f"\033[31mPicture #{id} not found\033[0m")

    def __photo_handler(self, id):
        self.config.p_build_photos.mkdir(parents=True, exist_ok=True)
        file = f"{id}.png"
        try:
            shutil.copyfile(self.config.p_data_photos / file, self.config.p_build_photos / file)
            if (self.config.p_data_photos / f"{id}.txt").exists():
                return (self.config.p_data_photos / f"{id}.txt").read_text()
            else:
                return "Bildbeschreibung noch nicht verfügbar"
        except FileNotFoundError:
            tqdm.write(f"\033[31mPhoto #{id} not found\033[0m")

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
        with (self.config.p_data_html / f"{include}.html").open() as file:
            return file.read()

    def __build_section(
        self,
        edition,
        edition_name,
        section,
        section_id,
        chapter,
        next_section=None,
        next_chapter=None,
        chapter_number=None,
    ):
        section_template = self.env.get_template("html/section.html")
        next_section_template = self.env.get_template("html/next_section.html")
        next_chapter_template = self.env.get_template("html/next_chapter.html")
        with (self.config.p_build / f"{edition}_{section['ident']}.html").open("w") as file:
            # Use provided chapter_number or fall back to chapter dict
            chapter_num = str(chapter_number) if chapter_number is not None else chapter.get("number", "0")
            section_num = str(section_id)

            # Set the section URL for references
            section_filename = f"{edition}_{section['ident']}.html"

            with FiftyOhmHtmlRenderer(
                question_renderer=self.__build_question,
                picture_handler=self.__picture_handler,
                photo_handler=self.__photo_handler,
                include_handler=self.__include_handler,
                edition=edition,
                chapter=chapter_num,
                section=section_num,
                section_url=section_filename,
            ) as renderer:
                # First pass: collect all figures and assign hierarchical numbers
                doc = Document(section["content"])
                renderer.collect_figures(doc)

                # Second pass: render with hierarchical numbers
                section["content"] = renderer.render(doc)

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

    def __build_chapter_slidedeck(self, edition, chapter, sections, next_chapter, chapter_number=None):
        with (self.config.p_build / f"{edition}_slide_{chapter['ident']}.html").open("w") as file:
            slide_template = self.env.get_template("slide/slide.html")
            help_template = self.env.get_template("slide/help.html")
            next_template = self.env.get_template("slide/next.html")

            # Use provided chapter_number or fall back to chapter dict
            chapter_num = str(chapter_number) if chapter_number is not None else chapter.get("number", "0")

            # Set the slide URL for references (all sections in one file)
            # Note: filename uses original edition (e.g., "N"), not modified edition with "S" (e.g., "NS")
            slide_filename = f"{edition}_slide_{chapter['ident']}.html"

            with FiftyOhmHtmlSlideRenderer(
                question_renderer=self.__build_question_slide,
                picture_handler=self.__picture_handler,
                photo_handler=self.__photo_handler,
                include_handler=self.__include_handler,
                edition=edition,
                chapter=chapter_num,
                section="0",  # Will be updated per section
                section_url=slide_filename,
            ) as renderer:
                result = "<section>\n"
                result += f'<section data-background="#DAEEFA">\n<h1>{chapter["title"]}</h1>\n</section>\n'
                result += help_template.render()
                result += "</section>\n"

                section_counter = 0
                for section in sections:
                    if section["slide"] is None:
                        continue

                    section_counter += 1
                    # Update section number for this section
                    renderer.section = str(section_counter)
                    # Reset figure counter for each section
                    renderer.figure_counter = 0
                    renderer.figure_map = {}

                    if not section["slide"].startswith("---"):
                        section["slide"] = "---\n" + section["slide"]

                    # First pass: collect figures
                    doc = Document(section["slide"])
                    renderer.collect_figures(doc)

                    # Second pass: render with hierarchical numbers
                    tmp = f'<section data-background="#DAEEFA">\n<h1>{section["title"]}</h1>\n</section>\n'
                    tmp += renderer.render(doc)
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

        with (self.config.p_data_toc / f"{edition}.json").open() as file:
            book = json.load(file)
            chapters = book["chapters"]

            for chapter in chapters:
                for section in chapter["sections"]:
                    ident = section["ident"]
                    section["content"] = None
                    section["slide"] = None
                    with (self.config.p_data_sections / f"{ident}.md").open() as sfile:
                        section_content = sfile.read()
                        section["content"] = section_content
                    with (self.config.p_data_slides / f"{ident}.md").open() as sfile:
                        section_content = sfile.read()
                        section["slide"] = section_content

            edition_name = book["title"]
            self.__build_book_index(book)
            self.__build_slide_index(book)
            for chapter_number, chapter in enumerate(tqdm(chapters, desc=f"Build Edition: {edition}"), 1):
                next_chapter = chapters[chapter_number] if chapter_number < len(chapters) else None
                self.__build_chapter(edition, edition_name, chapter_number, chapter, next_chapter)
                self.__build_chapter_slidedeck(edition, chapter, chapter["sections"], next_chapter, chapter_number)

                for section_number, section in enumerate(chapter["sections"], 1):
                    tqdm.write(f"Rendering section {section['title']}")
                    next_section = (
                        chapter["sections"][section_number] if section_number < len(chapter["sections"]) else None
                    )
                    self.__build_section(
                        edition,
                        edition_name,
                        section,
                        section_number,
                        chapter,
                        next_section,
                        next_chapter,
                        chapter_number,
                    )

    def build_assets(self):
        self.config.p_build.mkdir(exist_ok=True)
        shutil.copytree(
            self.config.p_assets, self.config.p_build_assets, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git")
        )

    def __parse_snippets(self):
        snippets = {}

        for md_file in Path(self.config.p_data_snippets).glob("*.md"):
            with md_file.open() as file:
                snippets[md_file.stem] = file.read()

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
        static = []

        for static_file in Path(self.config.p_data_static).glob("*.html"):
            if "sidebar" not in static_file.stem:
                with static_file.open() as file:
                    content = file.read()
                sidebar_file = self.config.p_data_static / f"{static_file.stem}_sidebar.html"
                if not sidebar_file.exists():
                    sidebar = ""
                else:
                    with sidebar_file.open() as file:
                        sidebar = file.read()

                static.append(
                    {
                        "url_part": static_file.stem,
                        "content": content,
                        "sidebar": sidebar if sidebar != "" else None,
                    }
                )
        return static

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

    def build_brightspots(self):
        for brightspot_file in self.config.p_data_brightspots.glob("*.md"):
            with brightspot_file.open() as file:
                content = file.read()
                with (self.config.p_build / f"{brightspot_file.stem}.html").open("w") as file:
                    with FiftyOhmHtmlRenderer(
                        question_renderer=functools.partial(
                            self.__build_question,
                            template_file="html/brightspot_question.html",
                        ),
                        picture_handler=self.__picture_handler,
                        photo_handler=self.__photo_handler,
                        include_handler=self.__include_handler,
                    ) as renderer:
                        brightspot_template = self.env.get_template("html/brightspot.html")
                        result = renderer.render(Document(content))
                        result = brightspot_template.render(content=result, number=brightspot_file.stem)
                        result = self.__build_page(result, course_wrapper=False)
                        file.write(result)
