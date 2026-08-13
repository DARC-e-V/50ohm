import json
import os
import re
import shutil
import zipfile
from abc import ABC, abstractmethod
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from ohm_renderer.index import Index, index_anchor_id
from ohm_renderer.question import Question
from rich.control import Control
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn, TimeRemainingColumn
from rich.segment import ControlType
from tqdm import tqdm

from .config import Config
from .question import QuestionCatalog, parse_questions

MISSING_ALT_TEXT = "Bildbeschreibung noch nicht verfügbar"

# Includes are raw HTML, so the pictures in them are plain <img> sources rather than tokens.
PICTURE_REFERENCE_PATTERN = re.compile(r"(\d+)\.svg")


@contextmanager
def progress_display() -> Generator[Progress]:
    progress = Progress(
        TaskProgressColumn(),
        BarColumn(),
        TimeRemainingColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    )

    with progress:
        yield progress

    if progress.console.is_terminal:
        progress.console.control(Control((ControlType.CURSOR_UP, 1), (ControlType.ERASE_IN_LINE, 2)))


@dataclass(frozen=True)
class ChapterContext:
    edition: str
    edition_name: str
    chapter: dict
    number: int
    next_chapter: dict | None


@dataclass(frozen=True)
class SectionContext:
    chapter: ChapterContext
    section: dict
    number: int
    next_section: dict | None
    content: str


class Builder(ABC):
    def __init__(self, config: Config):
        self.config = config

        self.question_index = {}
        self.keyword_index = {}

        self._alt_texts: dict[tuple[str, str], str | None] = {}
        self._includes: dict[str, str] = {}

    @cached_property
    def questions(self) -> QuestionCatalog:
        return parse_questions(
            self.config.p_data_fragenkatalog,
            self.config.p_data_metadata,
            self.config.p_data_solutions,
        )

    # -- assets ------------------------------------------------------------

    def _copy_asset(self, id, suffix: str, label: str, source_dir, target_dir: Path) -> str | None:
        if (label, id) in self._alt_texts:
            return self._alt_texts[label, id]

        file_name = f"{id}{suffix}"
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_dir / file_name, target_dir / file_name)
        except FileNotFoundError:
            tqdm.write(f"\033[31m{label} #{id} not found\033[0m")
            alt_text = None
        else:
            description = source_dir / f"{id}.txt"
            alt_text = description.read_text(encoding="utf-8") if description.exists() else MISSING_ALT_TEXT

        # Cache the alt text so the asset files are processed only once.
        self._alt_texts[label, id] = alt_text
        return alt_text

    def _picture_handler(self, id) -> str | None:
        return self._copy_asset(id, ".svg", "Picture", self.config.p_data_pictures, self.config.p_build_pictures)

    def _photo_handler(self, id) -> str | None:
        return self._copy_asset(id, ".png", "Photo", self.config.p_data_photos, self.config.p_build_photos)

    def _include_handler(self, ident) -> str:
        if ident in self._includes:
            return self._includes[ident]

        # Collect referenced pictures in the include and run them through the regular asset handler.
        code = (self.config.p_data_html / f"{ident}.html").read_text(encoding="utf-8")
        for id in PICTURE_REFERENCE_PATTERN.findall(code):
            self._picture_handler(id)

        # Cache the code so the include is read only once.
        self._includes[ident] = code
        return code

    # -- traversal ---------------------------------------------------------

    def build_edition(self, edition: str, progress: Progress | None = None) -> None:
        # Create a default progress if none is provided.
        if progress is None:
            with progress_display() as own_progress:
                self.build_edition(edition, own_progress)
            return

        self.config.p_build.mkdir(parents=True, exist_ok=True)

        edition = edition.upper()
        book = json.loads((self.config.p_data_toc / f"{edition}.json").read_text(encoding="utf-8"))
        chapters = book["chapters"]

        chapter_task = progress.add_task(f"Building edition {edition} ...")
        try:
            self._write_edition_index(book, edition)

            for number, chapter in enumerate(progress.track(chapters, task_id=chapter_task), 1):
                progress.update(chapter_task, description=f"Building edition {edition}: Chapter {chapter['title']}")

                ctx = ChapterContext(
                    edition=edition,
                    edition_name=book["title"],
                    chapter=chapter,
                    number=number,
                    # enumerate() starts at 1, so `number` is already the index of the next chapter.
                    next_chapter=chapters[number] if number < len(chapters) else None,
                )

                self._write_chapter_index(ctx)
                self._build_sections(ctx, progress)
                self._build_slides(ctx, progress)
        finally:
            # The display outlives this edition, so its task must not.
            progress.remove_task(chapter_task)

    def _build_sections(self, ctx: ChapterContext, progress: Progress) -> None:
        sections = ctx.chapter["sections"]
        written = 0

        section_task = progress.add_task(description="Rendering sections ...")
        for index, section in enumerate(progress.track(sections, task_id=section_task)):
            progress.update(section_task, description=f"Rendering section {section['title']}")

            content = (self.config.p_data_sections / f"{section['ident']}.md").read_text(encoding="utf-8")
            self._collect_question_occurrences(ctx, section, content)
            self._collect_index_occurrences(ctx, section, content)

            section_ctx = SectionContext(
                chapter=ctx,
                section=section,
                # The number it would get; only a section that renders actually consumes one.
                number=written + 1,
                next_section=sections[index + 1] if index + 1 < len(sections) else None,
                content=content,
            )

            body = self._render_section(section_ctx)
            if body is None:
                continue

            written += 1
            self._write_section(section_ctx, body)

        progress.remove_task(section_task)

    def _build_slides(self, ctx: ChapterContext, progress: Progress) -> None:
        slides = []
        slides_task = None

        for section in ctx.chapter["sections"]:
            slide = self._render_slide(ctx, section, len(slides) + 1)
            if slide is None:
                continue

            # Only a format that actually renders slides gets a progress bar for them.
            if slides_task is None:
                slides_task = progress.add_task("Rendering slides ...", total=len(ctx.chapter["sections"]))
            progress.update(slides_task, description=f"Rendering slides of {section['title']}", advance=1)

            slides.append(slide)

        if slides_task is not None:
            progress.remove_task(slides_task)

        self._write_slidedeck(ctx, slides)

    # -- output hooks ------------------------------------------------------

    @abstractmethod
    def _write_edition_index(self, book: dict, edition: str) -> None:
        """Writes the overview of the whole edition."""

    @abstractmethod
    def _write_chapter_index(self, ctx: ChapterContext) -> None:
        """Writes the overview of one chapter."""

    @abstractmethod
    def _render_section(self, ctx: SectionContext) -> str | None:
        """Renders the body of one section, or returns None to skip it."""

    @abstractmethod
    def _write_section(self, ctx: SectionContext, body: str) -> None:
        """Writes the rendered section to its file."""

    @abstractmethod
    def _render_slide(self, ctx: ChapterContext, section: dict, number: int) -> str | None:
        """Renders the slides of one section, or returns None when this format has none."""

    @abstractmethod
    def _write_slidedeck(self, ctx: ChapterContext, slides: list[str]) -> None:
        """Writes the slides of a chapter as one deck."""

    # -- build steps -------------------------------------------------------

    @abstractmethod
    def build_website(self) -> None:
        """Builds the pages surrounding the course."""

    @abstractmethod
    def build_solutions(self) -> None:
        """Builds one page per solution."""

    @abstractmethod
    def build_assets(self) -> None:
        """Copies the static assets into the build directory."""
        # TODO: Move into HTML builder only.

    # -- search indices ----------------------------------------------------

    @property
    @abstractmethod
    def _index_output_dir(self) -> Path:
        """Where the search indices are written to."""

    def _collect_question_occurrences(self, ctx: ChapterContext, section: dict, content: str) -> None:
        for question_number in Question.pattern.findall(content):
            if question_number not in self.question_index:
                question = self.questions.get(question_number)
                self.question_index[question_number] = {
                    # A question the pool does not know can still have a solution page.
                    "has_solution": question.has_solution
                    if question
                    else (self.config.p_data_solutions / f"{question_number}.md").exists(),
                    "section": section["ident"],
                    "chapter_title": ctx.chapter["title"],
                    "section_title": section["title"],
                    "editions": [],
                }

            editions = self.question_index[question_number]["editions"]
            if ctx.edition not in editions:
                editions.append(ctx.edition)

    def _collect_index_occurrences(self, ctx: ChapterContext, section: dict, content: str) -> None:
        for match in Index.pattern.finditer(content):
            first = match.group(1).strip()
            second = match.group(2).strip() if match.group(2) else None

            anchor_id = index_anchor_id(first, second)

            entry_key = f"{section['ident']}#{anchor_id}"
            keyword_entry = self.keyword_index.setdefault(
                entry_key,
                {
                    "term": first,
                    "subterm": second,
                    "anchor_id": anchor_id,
                    "section": section["ident"],
                    "chapter_title": ctx.chapter["title"],
                    "section_title": section["title"],
                    "editions": [],
                },
            )
            if ctx.edition not in keyword_entry["editions"]:
                keyword_entry["editions"].append(ctx.edition)

    def _write_index_file(self, name: str, data, sort_keys: bool = False) -> None:
        self._index_output_dir.mkdir(parents=True, exist_ok=True)
        with (self._index_output_dir / name).open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2, sort_keys=sort_keys)
            file.write("\n")

    def build_question_index(self) -> None:
        tqdm.write("Creating question index")
        for question_data in self.question_index.values():
            question_data["editions"] = sorted(question_data["editions"])

        self._write_index_file("question_index.json", self.question_index, sort_keys=True)

    def build_index(self) -> None:
        tqdm.write("Creating index")
        for index_data in self.keyword_index.values():
            index_data["editions"] = sorted(index_data["editions"])

        entries = sorted(
            self.keyword_index.values(),
            key=lambda item: (
                item["term"].casefold(),
                (item["subterm"] or "").casefold(),
                item["section"],
                item["anchor_id"],
            ),
        )

        self._write_index_file("index.json", entries)


def build_zip(config: Config, zip_name: str | None = None) -> Path:
    build_dir = config.p_build
    build_dir.mkdir(parents=True, exist_ok=True)

    zip_name = zip_name if zip_name is not None else f"{build_dir.name}.zip"
    zip_path = build_dir / zip_name

    # If a previous archive exists, remove it first to avoid zipping stale data.
    if zip_path.exists():
        zip_path.unlink()

    tqdm.write(f"Creating zip archive: {zip_path.resolve()}")

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # os.walk includes dotfiles; sort for stable archives.
        for root, dirs, files in os.walk(build_dir):
            dirs.sort()
            files.sort()

            root_path = Path(root)
            for filename in files:
                # The archive sits directly in the build directory, so it must not include itself.
                if root_path == build_dir and filename == zip_name:
                    continue

                file_path = root_path / filename
                zf.write(file_path, arcname=file_path.relative_to(build_dir))

    return zip_path
