import re

from renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from renderer.morse import Morse

from .slide_break import SlideBreak


class FiftyOhmLaTeXSlideRenderer(FiftyOhmLaTeXRenderer):
    @staticmethod
    def _replace_textrm_with_mathrm(text):
        """
        Ersetzt $..._\\textrm{...}...$ durch $..._{\\mathrm{...}}...$ in Math-Umgebungen.
        """

        # Ersetze nur im Math-Mode (also innerhalb von $...$)
        def replacer(match):
            expr = match.group(1)
            # Ersetze _\textrm{...} durch _{\mathrm{...}}
            expr = re.sub(r"_\\textrm\{([^}]*)\}", r"_{\\mathrm{\1}}", expr)
            return f"${expr}$"

        # Suche nach $...$
        return re.sub(r"\$(.*?)\$", replacer, text)

    @staticmethod
    def _convert_displaymath(text):
        """
        Wandelt Zeilen, die exakt aus $...$ bestehen (ohne weitere Zeichen), in $$...$$ um.
        Falls \begin{split} enthalten ist, wird stattdessen \\[ ... \\] verwendet.
        """

        def repl(line):
            stripped = line.strip()
            if (
                stripped.startswith("$")
                and stripped.endswith("$")
                and len(stripped) > 2
                and stripped.count("$") == 2
                and line == stripped  # keine Einrückung, keine weiteren Zeichen
            ):
                content = stripped[1:-1]
                if "\\begin{split}" in content:
                    return "\\[" + content + "\\]"
                else:
                    return "$$" + content + "$$"
            return line

        # Zeilenweise anwenden
        return "\n".join(repl(l) for l in text.split("\n"))

    def render_document(self, token):
        self.footnotes.update(token.footnotes)
        output = []
        # Zu Beginn: Falls kein Frame offen ist, Frame öffnen
        if not getattr(self, "_frame_open", False):
            output.append("\\begin{frame}[fragile]{~}")
            self._frame_open = True
        inner = self.render_inner(token)
        # Ersetze \textrm durch \mathrm im Math-Mode
        inner = self._replace_textrm_with_mathrm(inner)
        # Displaymath-Konvertierung NUR auf Top-Level anwenden
        inner = self._convert_displaymath(inner)
        output.append(inner)
        # Am Ende: Falls Frame noch offen, schließen
        if getattr(self, "_frame_open", False):
            output.append("\\end{frame}")
            self._frame_open = False
        return "\n".join(output)

    # Sorted (em_threshold, latex_command) pairs.
    # For a given em value, the first entry whose threshold is >= the value is chosen.
    _FONT_SIZE_SCALE = [
        (0.50, "\\tiny"),  # <= 0.50em
        (0.60, "\\scriptsize"),  # <= 0.60em
        (0.80, "\\footnotesize"),  # <= 0.80em
        (0.90, "\\small"),  # <= 0.90em
    ]

    def __init__(self, question_renderer=None, **kwargs):
        super().__init__(SlideBreak, question_renderer=question_renderer)
        self._in_columns = False
        self._frame_open = False  # Track if a frame is currently open

        # Add "S" suffix to edition for slides
        if getattr(self, "edition", None):
            self.edition = f"{self.edition}S"

    @staticmethod
    def _parse_font_size(attribute):
        """Extract LaTeX font size command from a style attribute string."""
        match = re.search(r"font-size:\s*([0-9.]+)em", attribute)
        if match:
            value = float(match.group(1))
            for threshold, cmd in FiftyOhmLaTeXSlideRenderer._FONT_SIZE_SCALE:
                if value <= threshold:
                    return cmd
            return None  # >= 1.0em → normalsize, no command needed
        # Handle keyword values like "smaller"
        if re.search(r"font-size:\s*smaller", attribute):
            return "\\small"
        return None

    def render_slide_break(self, token):
        attribute = getattr(token, "attribute", None) or ""

        # Convert data-background-iframe to a link slide
        if "data-background" in attribute:
            match = re.search(r'data-background-iframe="([^"]+)"', attribute)
            if match:
                url = match.group(1)
                out = ""
                if self._frame_open:
                    out += "\\end{frame}\n"
                out += f"\\begin{{frame}}[fragile]\n\\centering\\vfill\n\\href{{{url}}}{{\\texttt{{{url}}}}}\n\\vfill\n"
                self._frame_open = True
                return out
            return ""

        font_size = self._parse_font_size(attribute)
        title = None
        children = list(token.children)

        # Wenn das erste Kind eine Überschrift ist, nutze sie als Frame-Titel und entferne sie aus dem Inhalt
        self._suppress_next_heading = False
        if children:
            first = children[0]
            if hasattr(first, "__class__") and first.__class__.__name__ == "Heading":
                title = self.render_inner(first).strip()
                children = children[1:]
                self._suppress_next_heading = True

        inner = "".join(filter(lambda x: x is not None, [self.render(child) for child in children]))

        size_prefix = f"{font_size}\n" if font_size else ""

        out = ""
        if self._frame_open:
            out += "\\end{frame}\n"
        # Immer einen Frame-Titel setzen: entweder echten Titel oder ~ (auch wenn leer)
        frame_title = title if title and title.strip() else "~"
        out += f"\\begin{{frame}}[fragile]{{{frame_title}}}\n{size_prefix}{inner}\n"
        self._frame_open = True
        return out

    def render_qso(self, token):
        qso = ""
        for child in token.children:
            inner = self.render_inner(child)
            if child.received:
                qso += f"\\QSOother{{{inner}}}\n"
            else:
                qso += f"\\QSOown{{{inner}}}\n"
        return qso

    def render_tag(self, token):
        if token.tagtype == "fragment":
            inner = self.render_inner(token)
            return f"{inner}\n\\pause\n"
        if token.tagtype in ("left", "right"):
            inner = self.render_inner(token)
            if not self._in_columns:
                self._in_columns = True
                return f"\\begin{{Columns}}[T]\n\\Column{{0.50}}{{\n{inner}\n}}\n"
            else:
                self._in_columns = False
                return f"\\Column{{0.50}}{{\n{inner}\n}}\n\\end{{Columns}}\n"
        elif token.tagtype == "note":
            return ""

        return ""  # Ignore other tags in slide context anyway in tokenizer

    def render_heading(self, token):
        # Wenn die Flag _suppress_next_heading gesetzt ist, wird diese Heading nicht gerendert (sie war Frame-Titel)
        if getattr(self, "_suppress_next_heading", False):
            self._suppress_next_heading = False
            return ""
        inner = self.render_inner(token)
        return f"\\textbf{{{inner}}}\n"

    @staticmethod
    def render_morse_helper(morse_code):
        parts = []
        for i, char in enumerate(morse_code):
            if char == [3]:
                parts.append(r"\MorseWordSep{}")
            else:
                if i > 0 and morse_code[i - 1] != [3]:
                    parts.append(r"\MorseCharSep{}")
                symbols = []
                for symbol in char:
                    if symbol == 1:
                        symbols.append(r"\MorseDit{}")
                    elif symbol == 2:
                        symbols.append(r"\MorseDah{}")
                parts.append("".join(symbols))
        return "".join(parts)

    def render_morse(self, token):
        morse_code = Morse.convert_to_morse_code(token.content)
        return self.render_morse_helper(morse_code)

    @staticmethod
    def render_picture_helper(id, ref, text, number):
        result = rf"\DARCimage{{1.0\linewidth}}{{{id}}}"
        if text:
            # Ersetze Zeilenumbrüche durch LaTeX-Zeilenumbrüche
            safe_text = text.replace("\n", r"\\\n")
            result += f"\n\n\\begin{{centering}}\n{safe_text}\n\\end{{centering}}"
        return result

    def render_picture(self, token):
        return self.render_picture_helper(token.id, token.ref, token.text, token.number)

    @staticmethod
    def render_photo_helper(id, ref, text, number):
        result = rf"\includegraphics[width=1.0\linewidth,height=0.75\textheight,keepaspectratio]{{photo/{id}}}"
        if text:
            safe_text = text.replace("\n", r"\\\n")
            result += f"\n\n\\begin{{centering}}\n{safe_text}\n\\end{{centering}}"
        return result

    def render_table(self, token):
        table = "\n\\begin{DARCtabular}" + f"{self.render_inner(token)}" + "\\end{DARCtabular}"
        if getattr(token, "caption", None):
            safe_caption = token.caption.replace("\n", r"\\\n")
            table += f"\n\n\\begin{{centering}}\n{safe_caption}\n\\end{{centering}}"
        return table
