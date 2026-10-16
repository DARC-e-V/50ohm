import re
from pathlib import Path

import yaml
from ohm_renderer.document import Document
from ohm_renderer.fifty_ohm_mdx_renderer import FiftyOhmMdxRenderer
from ohm_renderer.tag import captures
from tqdm import tqdm

from .builder import Builder, ChapterContext, SectionContext
from .question import QuestionData

# The pool encodes the license class as a digit.
QUESTION_CLASSES = {"1": "N", "2": "E", "3": "A"}
BLOCK_TAG = re.compile(r"^<(/?)(" + "|".join(captures) + r")>$")


def normalize_block_tags(content: str, section_ident: str) -> str:
    """Give DARCdown block tags paragraph boundaries and ignore orphan closers.

    An orphan closing tag is a source defect. It is reported, but cannot be
    emitted as JSX because it would break the whole static site build.
    """
    opened: dict[str, int] = {}
    lines = []
    for line in content.splitlines():
        match = BLOCK_TAG.fullmatch(line.strip())
        if not match:
            lines.append(line)
            continue
        closing, tag = match.groups()
        if closing:
            if not opened.get(tag, 0):
                tqdm.write(f"Ignoring unmatched </{tag}> in section {section_ident}")
                continue
            opened[tag] -= 1
        else:
            opened[tag] = opened.get(tag, 0) + 1
        lines.extend(("", line.strip(), ""))
    return "\n".join(lines)


def present(meta: dict) -> dict:
    """Drops ``None`` values, so optional fields disappear instead of showing up as ``null``."""
    return {key: value for key, value in meta.items() if value is not None}


def collapse_whitespace(text: str | None) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def frontmatter(meta: dict) -> str:
    """Serializes metadata into a YAML frontmatter block.

    ``None`` values are dropped. The insertion order of the keys is kept, which makes the
    generated files readable and their diffs stable.
    """
    block = yaml.safe_dump(present(meta), allow_unicode=True, sort_keys=False, default_flow_style=False)
    return f"---\n{block}---\n\n"


class MdxBuilder(Builder):
    """Builds one MDX file per section, for a frontend to consume.

    Everything the HTML build resolves at build time and that the frontend can do better stays
    unresolved here: questions, includes and references become components. The question catalog
    is written once as data for the frontend to look the questions up in. Slides, the solution
    pages and the surrounding website are not implemented yet.
    """

    # -- output locations --------------------------------------------------

    @property
    def _index_output_dir(self) -> Path:
        return self.config.p_build / "_data"

    @property
    def _includes_dir(self) -> Path:
        return self.config.p_build / "includes"

    def _edition_dir(self, edition: str) -> Path:
        return self.config.p_build / edition

    def _chapter_dir(self, ctx: ChapterContext) -> Path:
        return self._edition_dir(ctx.edition) / ctx.chapter["ident"]

    @staticmethod
    def _write(path: Path, meta: dict, body: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(frontmatter(meta) + body.strip() + "\n", encoding="utf-8")

    # -- includes ----------------------------------------------------------

    def _include_handler(self, ident: str) -> str:
        # Ask the cache first: copying belongs to the one time the include is actually read.
        if ident in self._includes:
            return self._includes[ident]

        code = super()._include_handler(ident)

        self._includes_dir.mkdir(parents=True, exist_ok=True)
        (self._includes_dir / f"{ident}.html").write_text(code, encoding="utf-8")

        return code

    # -- edition and chapter overviews -------------------------------------

    def _write_edition_index(self, book: dict, edition: str) -> None:
        meta = {
            "title": book["title"],
            "edition": edition,
        }
        self._write(self._edition_dir(edition) / "index.mdx", meta, book["abstract"])

    def _write_chapter_index(self, ctx: ChapterContext) -> None:
        meta = {
            "title": ctx.chapter["title"],
            "ident": ctx.chapter["ident"],
            "edition": ctx.edition,
            "chapterNumber": ctx.number,
            "videoUrl": ctx.chapter.get("video_url") or None,
        }
        self._write(self._chapter_dir(ctx) / "index.mdx", meta, ctx.chapter["abstract"])

    # -- sections ----------------------------------------------------------

    def _render_section(self, ctx: SectionContext) -> str:
        # DARCdown permits a block tag directly after a paragraph without a
        # blank line. Mistletoe otherwise absorbs its opener into the paragraph,
        # leaving an unmatched closing tag for MDX to reject.
        content = normalize_block_tags(ctx.content, ctx.section["ident"])
        with FiftyOhmMdxRenderer(
            picture_handler=self._picture_handler,
            photo_handler=self._photo_handler,
            include_handler=self._include_handler,
            edition=ctx.chapter.edition,
            chapter=str(ctx.chapter.number),
            section=str(ctx.number),
        ) as renderer:
            return renderer.render(Document(content))

    def _write_section(self, ctx: SectionContext, body: str) -> None:
        section = ctx.section
        meta = {
            "title": section["title"],
            "ident": section["ident"],
            "edition": ctx.chapter.edition,
            "chapterIdent": ctx.chapter.chapter["ident"],
            "chapterNumber": ctx.chapter.number,
            "sectionNumber": ctx.number,
            "videoUrl": section.get("video_url") or None,
            "status": section.get("status"),
            "class": section.get("class"),
        }
        self._write(self._chapter_dir(ctx.chapter) / f"{section['ident']}.mdx", meta, body)

    # -- question catalog --------------------------------------------------

    def _question_picture(self, id) -> dict | None:
        """Copies a picture of a question and describes it, or returns None if it is missing."""
        alt_text = self._picture_handler(str(id))
        if alt_text is None:
            return None

        # JSON needs no Markdown escaping, so unlike render_image only the whitespace goes.
        return {"id": str(id), "alt": collapse_whitespace(alt_text)}

    def _question_entry(self, question: QuestionData) -> dict:
        """One question as the frontend reads it.

        The text stays source text (``$…$`` and ``<u>`` included), since escaping depends on the
        output. The answers keep the order of the pool, so the first one is the correct one.
        """
        answers = []
        for index in range(4):
            text = question.answers[index] if question.answers else ""
            picture = question.answer_pictures[index] if question.answer_pictures else ""
            answers.append(
                present(
                    {
                        "text": collapse_whitespace(text) or None,
                        "picture": self._question_picture(picture) if picture != "" else None,
                    }
                )
            )

        return present(
            {
                "class": QUESTION_CLASSES.get(question.question_class),
                "question": collapse_whitespace(question.text),
                "picture": self._question_picture(question.picture_question)
                if question.picture_question != ""
                else None,
                "answers": answers,
                # The meaning of the codes lives in the CSS only, so pass them through as they are.
                "layout": question.layout or None,
            }
        )

    def build_questions(self) -> None:
        """Writes the whole catalog, not only the questions the sections use.

        Solution pages and later features such as a trainer refer to any question, and the file
        is only read at build time.
        """
        tqdm.write("Creating question catalog")
        catalog = {number: self._question_entry(question) for number, question in self.questions.items()}
        self._write_index_file("questions.json", catalog, sort_keys=True)

    # -- deliberately not implemented --------------------------------------

    def _render_slide(self, ctx: ChapterContext, section: dict, number: int) -> None:
        """No slides in MDX yet. Returning None here keeps contents/slides/ unread."""
        return None

    def _write_slidedeck(self, ctx: ChapterContext, slides: list[str]) -> None:
        """No slides in MDX yet, and _render_slide never produces any to write."""

    def build_website(self) -> None:
        """The pages surrounding the course are still built as HTML only."""

    def build_solutions(self) -> None:
        """The solution pages are still built as HTML only."""

    def build_assets(self) -> None:
        """The frontend consuming the MDX brings its own assets, so there is nothing to copy.

        The pictures and photos the sections reference are copied by the asset handlers while
        rendering, independently of this step.
        """
