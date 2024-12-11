import mistletoe

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from test.util import paragraph


def test_underline_html():
    assertions = {
        "<u>Text</u>": "<u>Text</u>",
        "<u> Text Text </u>": "<u> Text Text </u>",
        "<u> Text *Text* </u>": "<u> Text <em>Text</em> </u>",
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlRenderer) == paragraph(assertions[assertion])


def test_underline_latex():
    assertions = {
        "<u>Text</u>": "\n\\underline{Text}\n",
        "<u> Text Text </u>": "\n\\underline{ Text Text }\n",
        "<u> Text *Text* </u>": "\n\\underline{ Text \emph{Text} }\n",
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmLaTeXRenderer) == assertions[assertion]
