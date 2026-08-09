import mistletoe
import pytest
from ohm_renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from util import paragraph, render_html, render_mdx


@pytest.mark.html
def test_underline_html():
    assertions = {
        "<u>Text</u>": "<u>Text</u>",
        "<u> Text Text </u>": "<u> Text Text </u>",
        "<u> Text *Text* </u>": "<u> Text <em>Text</em> </u>",
    }

    for assertion in assertions:
        assert render_html(assertion) == paragraph(assertions[assertion])


@pytest.mark.mdx
def test_underline_mdx():
    # <u> is valid JSX, so the markup survives and its children stay Markdown.
    assertions = {
        "<u>Text</u>": "<u>Text</u>\n",
        "<u> Text Text </u>": "<u> Text Text </u>\n",
        "<u> Text *Text* </u>": "<u> Text *Text* </u>\n",
    }

    for assertion in assertions:
        assert render_mdx(assertion) == assertions[assertion]


@pytest.mark.latex
def test_underline_latex():
    assertions = {
        "<u>Text</u>": "\n\\underline{Text}\n",
        "<u> Text Text </u>": "\n\\underline{ Text Text }\n",
        "<u> Text *Text* </u>": "\n\\underline{ Text \\emph{Text} }\n",
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmLaTeXRenderer) == assertions[assertion]
