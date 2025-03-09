import mistletoe
import pytest

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from test.util import paragraph


@pytest.mark.html
def test_picture_html():
    assertions = {
        "[picture:123:abc:Text]": FiftyOhmHtmlRenderer.render_picture_helper("123", "abc", "Text", "TODO"),
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlRenderer) == paragraph(assertions[assertion])


#@pytest.mark.latex
#def test_underline_latex():
#    assertions = {
#        "<u>Text</u>": "\n\\underline{Text}\n",
#        "<u> Text Text </u>": "\n\\underline{ Text Text }\n",
#        "<u> Text *Text* </u>": "\n\\underline{ Text \emph{Text} }\n",
#    }
#
#    for assertion in assertions:
#        assert mistletoe.markdown(assertion, FiftyOhmLaTeXRenderer) == assertions[assertion]
