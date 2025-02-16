import mistletoe
import pytest

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from test.util import paragraph


@pytest.mark.html
def test_comment_html():
    assertions = {
        # TODOD: Remove \n
        "%Comment\nBar": paragraph("Bar"),
        "%Comment\n": "",
        "Foo 100 % Bar": paragraph("Foo 100% Bar"),
        "Foo\n%Comment\nBar": paragraph("Foo") + paragraph("Bar"),
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlRenderer) == assertions[assertion]


@pytest.mark.latex
def test_comment_latex():
    assertions = {
        "%Comment\nBar": "% Comment\nBar\n",
        "%Comment\n": "% Comment",
        "Foo 100 % Bar": "\nFoo 100 \% Bar\n",
        "Foo\n%Comment\nBar": "\nFoo\n% Comment\nBar\n",
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmLaTeXRenderer) == assertions[assertion]
