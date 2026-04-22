import json
import random
import shutil
import subprocess
from pathlib import Path

from mistletoe import Document

from renderer.fifty_ohm_latex_slide_renderer import FiftyOhmLaTeXSlideRenderer

from .config import Config
from .edition import Edition


class LatexSlidesBuild:
    def __init__(self, config: Config):
        self.config = config
        self.questions = self._parse_question_pool()
        self.metadata = self._load_metadata()
        self.question_metadata = self._load_question_metadata()

    def _parse_question_pool(self) -> dict:
        with self.config.p_data_fragenkatalog.open(encoding="utf-8") as file:
            fragenkatalog = json.load(file)

        questions = {}
        for exampart in fragenkatalog.get("sections", []):
            for chapter in exampart.get("sections", []):
                for question in chapter.get("questions", []):
                    questions[question["number"]] = question
                for section in chapter.get("sections", []):
                    for question in section.get("questions", []):
                        questions[question["number"]] = question

        return questions

    def _load_metadata(self) -> dict:
        with self.config.p_data_metadata.open(encoding="utf-8") as file:
            return json.load(file)

    def _load_question_metadata(self) -> dict:
        with self.config.p_data_question_metadata.open(encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def _normalize_edition(edition: str | Edition) -> str:
        if isinstance(edition, Edition):
            return edition.value
        return str(edition).upper()

    def _picture_command(self, number, field, scale):
        meta = self.metadata.get(number, {})
        picture = meta.get(f"picture_{field}")

        # TODO Wickelkondensator

        if not picture:
            return ""
        else:
            return f"\\DARCimage{{{scale}\\linewidth}}{{{picture}}}"

    @staticmethod
    def _escape_latex(text: str) -> str:
        text = text.replace("%", r"\%")
        return text

    def _render_question(self, number: str) -> str:
        question = self.questions.get(number)
        if question is None:
            return rf"\textbf{{Frage {number}}}"

        qtype = "Question"
        qscale = 1.0
        ascale = 1.0

        if number in self.question_metadata:
            qtype = self.question_metadata[number]["type"]
            qscale = self.question_metadata[number]["qscale"]
            ascale = self.question_metadata[number]["ascale"]

        picture_question = self._picture_command(number, "question", qscale)
        question_text = self._escape_latex(question.get("question") or "")
        question_id = question.get("number", number)

        # Build (answer_text, picture, is_correct) tuples; answer A is always correct
        answers = [
            (self._escape_latex(question.get("answer_a") or ""), self._picture_command(number, "a", ascale), True),
            (self._escape_latex(question.get("answer_b") or ""), self._picture_command(number, "b", ascale), False),
            (self._escape_latex(question.get("answer_c") or ""), self._picture_command(number, "c", ascale), False),
            (self._escape_latex(question.get("answer_d") or ""), self._picture_command(number, "d", ascale), False),
        ]

        # Deterministic shuffle per question
        rng = random.Random(number)
        rng.shuffle(answers)

        def _format_answers(bold_correct):
            parts = []
            for text, pic, correct in answers:
                if bold_correct and correct:
                    parts.append(f"\t{{\\textbf{{{text}}}{pic}}}")
                else:
                    parts.append(f"\t{{{text}{pic}}}")
            return "\n".join(parts)

        header = f"\\{qtype}{{{question_id}}}\n\t{{{question_text}}}\n\t{{{picture_question}}}\n"

        overlay1 = f"\\only<1>{{\n{header}{_format_answers(False)}\n}}\n"
        overlay2 = f"\\only<2>{{\n{header}{_format_answers(True)}\n}}\n"

        return overlay1 + overlay2

    def _load_toc(self, edition: str) -> dict:
        toc_path = self.config.p_data_toc / f"{edition}.json"
        with toc_path.open(encoding="utf-8") as file:
            return json.load(file)

    def _read_slide(self, ident: str) -> str:
        slide_path = self.config.p_data_slides / f"{ident}.md"
        with slide_path.open(encoding="utf-8") as file:
            return self._normalize_slide_tags(file.read())

    @staticmethod
    def _normalize_slide_tags(markdown: str) -> str:
        """Ensure custom slide tags are separated as block-level lines.

        Without surrounding blank lines, mistletoe can absorb tag lines into a
        preceding paragraph (for example after [picture:...]).
        """
        tag_lines = {
            "<left>",
            "</left>",
            "<right>",
            "</right>",
            "<note>",
            "</note>",
            "<fragment>",
            "</fragment>",
        }

        lines = markdown.splitlines()
        normalized: list[str] = []

        for line in lines:
            stripped = line.strip()
            if stripped in tag_lines:
                if normalized and normalized[-1].strip() != "":
                    normalized.append("")
                normalized.append(stripped)
                continue

            normalized.append(line)

        return "\n".join(normalized) + ("\n" if markdown.endswith("\n") else "")

    def _render_slide_markdown(self, markdown: str) -> str:
        with FiftyOhmLaTeXSlideRenderer(question_renderer=self._render_question) as renderer:
            return renderer.render(Document(markdown))

    def _write_section_file(self, output_dir: Path, section_ident: str, section_title: str):
        slide_markdown = self._read_slide(section_ident)
        if not slide_markdown.strip():
            return

        rendered = self._render_slide_markdown(slide_markdown)
        section_file = output_dir / f"section-{section_ident}.tex"

        # Always prepend a dedicated title slide for each section
        content = [
            f"% Auto-generated section slides for {section_ident}",
            r"\begin{frame}[fragile]",
            r"\vfill",
            r"\centering",
            r"\begin{beamercolorbox}[sep=8pt,center]{section title box}",
            rf"\hypersetup{{hidelinks}}\usebeamerfont{{title}}{section_title}\par%",
            r"\end{beamercolorbox}",
            r"\vfill",
            r"\end{frame}",
            rendered,
            "",
        ]

        with section_file.open("w", encoding="utf-8") as file:
            file.write("\n".join(content))

    def generate_edition(self, edition: str | Edition) -> None:
        """Generate LaTeX slide include file for one edition.

        Output structure:
        build/tex/section-<ident>.tex
        build/tex/slide-<EDITION>.tex
        """

        edition_code = self._normalize_edition(edition)
        book = self._load_toc(edition_code)

        output_dir = self.config.p_build_latex
        output_dir.mkdir(parents=True, exist_ok=True)

        written_sections: set[str] = set()
        lines: list[str] = [
            f"% Auto-generated LaTeX slides for edition {edition_code}",
            r"\PassOptionsToPackage{full}{textcomp}",
            r"\documentclass[aspectratio = 169]{beamer}",
            "",
            r"\usetheme{darc}",
            r"\input{settings-latex-slide.tex}",
            r"\input{settings.tex}",
            "",
            r"\begin{document}",
            "",
            rf"\title{{DARC Amateurfunklehrgang Klasse {edition_code}}}",
            r"\institute{Deutscher Amateur Radio Club e.\,V.}",
            r"\begin{frame}",
            r"\maketitle",
            r"\end{frame}",
        ]

        for chapter in book.get("chapters", []):
            chapter_title = chapter.get("title", "")

            lines.append(f"\n\\section{{{chapter_title}}}\n")
            lines.append(r"\begin{frame}[fragile]")
            lines.append(r"\vfill")
            lines.append(r"\centering")
            lines.append(r"\begin{beamercolorbox}[sep=8pt,center]{section title box}")
            lines.append(rf"\hypersetup{{hidelinks}}\usebeamerfont{{title}}{chapter_title}\par%")
            lines.append(r"\end{beamercolorbox}")
            lines.append(r"\vfill")
            lines.append(r"\end{frame}")

            for section in chapter.get("sections", []):
                section_ident = section["ident"]
                section_title = section.get("title", section_ident)

                if section_ident not in written_sections:
                    self._write_section_file(output_dir, section_ident, section_title)
                    written_sections.add(section_ident)

                lines.append(rf"\input{{section-{section_ident}}}")

            lines.append("")

        lines.append(r"\end{document}")
        lines.append("")

        slide_file = output_dir / f"slide-{edition_code}.tex"
        with slide_file.open("w", encoding="utf-8") as file:
            file.write("\n".join(lines))

    def copy_assets(self):

        # Copy Style and Settings:

        files = [
            "beamerthemedarc.sty",
            "settings.tex",
            "settings-latex-slide.tex",
            "world.png",
            "50ohm.pdf",
            "DARCLogo.pdf",
        ]

        path = self.config.p_latex
        self.config.p_build_latex.mkdir(parents=True, exist_ok=True)

        for file in files:
            source = path / file
            target = self.config.p_build_latex / file
            if source.exists():
                shutil.copy2(source, target)
            else:
                print(f"WARN missing LaTeX asset: {source}")

        # Copy Drawings:
        target_dir = self.config.p_build_latex / "img"
        target_dir.mkdir(parents=True, exist_ok=True)
        for source in self.config.p_data_pictures.glob("*.tex"):
            target = target_dir / source.name
            shutil.copy2(source, target)

        # Copy Photos:
        target_dir = self.config.p_build_latex / "photo"
        target_dir.mkdir(parents=True, exist_ok=True)
        for source in self.config.p_data_photos.glob("*.*"):
            target = target_dir / source.name
            shutil.copy2(source, target)

        # Symlink photos, so LaTeX can access these assets to render into graphics.
        foto_link = self.config.p_build_latex / "foto"
        if not foto_link.exists() and not foto_link.is_symlink():
            foto_link.symlink_to("photo")

    def run_latex(self, edition: str | Edition) -> None:
        edition_code = self._normalize_edition(edition)
        tex_file = f"slide-{edition_code}.tex"

        latexmk = shutil.which("latexmk")
        if latexmk is None:
            print("WARN latexmk not found; skipping PDF build")
            return

        base_cmd = [
            latexmk,
            "-lualatex",
            # "-interaction=nonstopmode",
            "-halt-on-error",
            "-file-line-error",
            tex_file,
        ]

        try:
            subprocess.run(
                base_cmd,
                check=True,
                cwd=str(self.config.p_build_latex),
                timeout=300,
            )
        except subprocess.TimeoutExpired:
            print(f"WARN latexmk timed out for {tex_file}")
        except subprocess.CalledProcessError as error:
            # latexmk can cache a previous error and return exit 12 even when
            # nothing changed; force one clean rerun in that case.
            if error.returncode == 12:
                try:
                    subprocess.run(
                        [latexmk, "-g", *base_cmd[1:]],
                        check=True,
                        cwd=str(self.config.p_build_latex),
                        timeout=300,
                    )
                    return
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as retry_error:
                    print(f"WARN latexmk forced rerun failed for {tex_file}: {retry_error}")
                    return

            print(f"WARN latexmk failed for {tex_file}: {error}")
        except OSError as error:
            print(f"WARN latexmk failed for {tex_file}: {error}")

    def build_edition(self, edition: str | Edition) -> None:
        self.generate_edition(edition)
        self.copy_assets()
        self.run_latex(edition)
