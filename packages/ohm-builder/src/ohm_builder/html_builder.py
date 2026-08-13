import random
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from ohm_renderer.document import Document
from ohm_renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from ohm_renderer.fifty_ohm_html_slide_renderer import FiftyOhmHtmlSlideRenderer
from tqdm import tqdm

from .builder import Builder, ChapterContext, SectionContext
from .config import Config
from .question import QuestionData


class HtmlBuilder(Builder):
    """Builds the flat HTML site: course pages, slide decks, solutions and the landing pages."""

    def __init__(self, config: Config):
        super().__init__(config)

        # Templates are not expected to change mid-build, so we can disable auto-reload to drastically improved speed.
        self.env = Environment(loader=FileSystemLoader(self.config.p_templates), auto_reload=False)
        self.env.filters["shuffle_answers"] = self._filter_shuffle_answers

    @property
    def _index_output_dir(self) -> Path:
        # Next to the other assets, where suche.html fetches them from.
        return self.config.p_build_assets

    # -- questions ---------------------------------------------------------

    def _build_question(self, number, template_file="html/question.html") -> str:
        """Renders one question, including the alt texts of its pictures."""
        question = self.questions.get(number)
        if question is None:
            tqdm.write(f"\033[31mQuestion #{number} is missing{self.questions.missing_note(number)}\033[0m")
            question = QuestionData.not_found(number)

        alt_text_answers = [self._picture_handler(picture) for picture in question.answer_pictures]
        alt_text_question = self._picture_handler(question.picture_question) if question.picture_question else ""

        return self.env.get_template(template_file).render(
            question=question.text,
            number=question.number,
            layout=question.layout,
            picture_question=question.picture_question,
            answers=question.answers,
            answer_pictures=question.answer_pictures,
            alt_text_answers=alt_text_answers,
            alt_text_question=alt_text_question,
            has_solution=question.has_solution,
        )

    def _build_question_slide(self, number) -> str:
        return self._build_question(number, template_file="slide/question.html")

    def _filter_shuffle_answers(self, seq):
        # The first answer of the pool is the correct one.
        answers = [{"content": answer, "correct": index == 0} for index, answer in enumerate(seq)]
        random.shuffle(answers)
        return answers

    # -- renderer handlers -------------------------------------------------

    def _renderer_handlers(self, question_renderer=None) -> dict:
        return {
            "question_renderer": question_renderer or self._build_question,
            "picture_handler": self._picture_handler,
            "photo_handler": self._photo_handler,
            "include_handler": self._include_handler,
        }

    # -- page shell --------------------------------------------------------

    def _build_page(self, content, course_wrapper=False, sidebar=None) -> str:
        page_template = self.env.get_template("html/page.html")
        return page_template.render(content=content, course_wrapper=course_wrapper, sidebar=sidebar)

    # -- edition, chapter, section -----------------------------------------

    def _write_edition_index(self, book: dict, edition: str) -> None:
        for template_name, suffix in (
            ("html/course_index.html", "course_index"),
            ("slide/slide_index.html", "slide_index"),
        ):
            result = self.env.get_template(template_name).render(book=book)
            result = self._build_page(result)
            (self.config.p_build / f"{edition}_{suffix}.html").write_text(result, encoding="utf-8")

    def _write_chapter_index(self, ctx: ChapterContext) -> None:
        result = self.env.get_template("html/chapter.html").render(
            edition=ctx.edition,
            name=ctx.edition_name,
            number=ctx.number,
            chapter=ctx.chapter,
        )

        if ctx.next_chapter is not None:
            result += self.env.get_template("html/next_chapter.html").render(
                url=f"{ctx.edition}_chapter_{ctx.next_chapter['ident']}.html",
                title=ctx.next_chapter["title"],
            )

        result = self._build_page(result, course_wrapper=True)
        (self.config.p_build / f"{ctx.edition}_chapter_{ctx.chapter['ident']}.html").write_text(
            result, encoding="utf-8"
        )

    def _render_section(self, ctx: SectionContext) -> str:
        with FiftyOhmHtmlRenderer(
            **self._renderer_handlers(),
            edition=ctx.chapter.edition,
            chapter=str(ctx.chapter.number),
            section=str(ctx.number),
            section_url=f"{ctx.chapter.edition}_{ctx.section['ident']}.html",
        ) as renderer:
            return renderer.render(Document(ctx.content))

    def _write_section(self, ctx: SectionContext, body: str) -> None:
        edition = ctx.chapter.edition

        result = self.env.get_template("html/section.html").render(
            edition=edition,
            name=ctx.chapter.edition_name,
            # A shallow copy, so the table of contents keeps its unrendered content.
            section={**ctx.section, "content": body},
            section_id=ctx.number,
            chapter=ctx.chapter.chapter,
        )

        if ctx.next_section is not None:
            result += self.env.get_template("html/next_section.html").render(
                url=f"{edition}_{ctx.next_section['ident']}.html",
                title=ctx.next_section["title"],
            )
        elif ctx.chapter.next_chapter is not None:
            result += self.env.get_template("html/next_chapter.html").render(
                url=f"{edition}_chapter_{ctx.chapter.next_chapter['ident']}.html",
                title=ctx.chapter.next_chapter["title"],
            )

        result = self._build_page(result, course_wrapper=True)
        (self.config.p_build / f"{edition}_{ctx.section['ident']}.html").write_text(result, encoding="utf-8")

    # -- slides ------------------------------------------------------------

    def _render_slide(self, ctx: ChapterContext, section: dict, number: int) -> str | None:
        content = (self.config.p_data_slides / f"{section['ident']}.md").read_text(encoding="utf-8")
        if not content.startswith("---"):
            content = "---\n" + content

        with FiftyOhmHtmlSlideRenderer(
            **self._renderer_handlers(question_renderer=self._build_question_slide),
            edition=ctx.edition,
            chapter=str(ctx.number),
            section=str(number),
            section_url=f"{ctx.edition}_slide_{ctx.chapter['ident']}.html",
        ) as renderer:
            body = f'<section data-background="#DAEEFA">\n<h1>{section["title"]}</h1>\n</section>\n'
            body += renderer.render(Document(content))

        return f"<section>{body}</section>\n"

    def _write_slidedeck(self, ctx: ChapterContext, slides: list[str]) -> None:
        result = "<section>\n"
        result += f'<section data-background="#DAEEFA">\n<h1>{ctx.chapter["title"]}</h1>\n</section>\n'
        result += self.env.get_template("slide/help.html").render()
        result += "</section>\n"

        result += "".join(slides)

        result += self.env.get_template("slide/next.html").render(
            edition=ctx.edition,
            next_chapter=ctx.next_chapter,
            chapter=ctx.chapter,
        )

        result = self.env.get_template("slide/slide.html").render(content=result)
        (self.config.p_build / f"{ctx.edition}_slide_{ctx.chapter['ident']}.html").write_text(result, encoding="utf-8")

    # -- solutions ---------------------------------------------------------

    def build_solutions(self) -> None:
        for solution_file in self.config.p_data_solutions.glob("*.md"):
            content = solution_file.read_text(encoding="utf-8")
            with FiftyOhmHtmlRenderer(**self._renderer_handlers()) as renderer:
                question = self._build_question(solution_file.stem, template_file="html/solution_question.html")
                solution = renderer.render(Document(content))

            page = self.env.get_template("html/solution.html").render(
                question=question, solution=solution, number=solution_file.stem
            )
            page = self._build_page(page, course_wrapper=False)
            (self.config.p_build / f"{solution_file.stem}.html").write_text(page, encoding="utf-8")

    # -- surrounding website -----------------------------------------------

    def _parse_snippets(self) -> dict:
        snippets = {}

        for md_file in self.config.p_data_snippets.glob("*.md"):
            snippets[md_file.stem] = md_file.read_text(encoding="utf-8")

        with FiftyOhmHtmlRenderer(**self._renderer_handlers()) as renderer:
            for key, value in snippets.items():
                snippets[key] = renderer.render_inner(Document(value))
                # Remove leading <p> and trailing </p>:
                snippets[key] = snippets[key][3:-4]

        return snippets

    def _build_snippet_page(self, snippets: dict, template: str, page: str) -> None:
        result = self.env.get_template(f"html/{template}.html").render({"snippets": snippets})
        result = self._build_page(result)
        (self.config.p_build / f"{page}.html").write_text(result, encoding="utf-8")

    def _build_static_page(self, page: str) -> None:
        source = self.config.p_data_static / f"{page}.html"
        if not source.exists():
            return

        sidebar_file = self.config.p_data_static / f"{page}_sidebar.html"
        sidebar = sidebar_file.read_text(encoding="utf-8") if sidebar_file.exists() else None

        result = self._build_page(content=source.read_text(encoding="utf-8"), sidebar=sidebar or None)
        (self.config.p_build / f"{page}.html").write_text(result, encoding="utf-8")

    def build_website(self) -> None:
        self.config.p_build.mkdir(parents=True, exist_ok=True)

        snippets = self._parse_snippets()
        self._build_snippet_page(snippets, "index", "index")
        self._build_snippet_page(snippets, "kurse-karte", "kurse_vor_ort_karte")
        self._build_snippet_page(snippets, "kurse-liste", "kurse_vor_ort_liste")
        self._build_snippet_page(snippets, "patenkarte", "patenkarte")
        self._build_static_page("pruefung")
        self._build_static_page("infos")
        self._build_static_page("suche")

    # -- assets ------------------------------------------------------------

    def build_assets(self) -> None:
        self.config.p_build.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            self.config.p_assets, self.config.p_build_assets, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git")
        )
