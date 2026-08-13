from pathlib import Path

import yaml
from ohm_renderer.document import Document
from ohm_renderer.fifty_ohm_mdx_renderer import FiftyOhmMdxRenderer

from .builder import Builder, ChapterContext, SectionContext


def frontmatter(meta: dict) -> str:
    """Serializes metadata into a YAML frontmatter block.

    ``None`` values are dropped, so optional fields simply disappear instead of showing up as
    ``null``. The insertion order of the keys is kept, which makes the generated files readable
    and their diffs stable.
    """
    present = {key: value for key, value in meta.items() if value is not None}
    block = yaml.safe_dump(present, allow_unicode=True, sort_keys=False, default_flow_style=False)
    return f"---\n{block}---\n\n"


class MdxBuilder(Builder):
    """Builds one MDX file per section, for a frontend to consume.

    Everything the HTML build resolves at build time and that the frontend can do better stays
    unresolved here: questions, includes and references become components. Slides, the solution
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
        with FiftyOhmMdxRenderer(
            picture_handler=self._picture_handler,
            photo_handler=self._photo_handler,
            include_handler=self._include_handler,
            edition=ctx.chapter.edition,
            chapter=str(ctx.chapter.number),
            section=str(ctx.number),
        ) as renderer:
            return renderer.render(Document(ctx.content))

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
