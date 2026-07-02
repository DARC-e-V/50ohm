import mistletoe
import pytest
from ohm_renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from util import paragraph, render_html


@pytest.mark.html
def test_underline_html():
    assertions = {
        "<u>Text</u>": "<u>Text</u>",
        "<u> Text Text </u>": "<u> Text Text </u>",
        "<u> Text *Text* </u>": "<u> Text <em>Text</em> </u>",
    }

    for assertion in assertions:
        assert render_html(assertion) == paragraph(assertions[assertion])


@pytest.mark.latex
def test_underline_latex():
    assertions = {
        "<u>Text</u>": "\n\\underline{Text}\n",
        "<u> Text Text </u>": "\n\\underline{ Text Text }\n",
        "<u> Text *Text* </u>": "\n\\underline{ Text \\emph{Text} }\n",
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmLaTeXRenderer) == assertions[assertion]
