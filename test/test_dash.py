import mistletoe
import pytest

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from test.util import paragraph


@pytest.mark.html
def test_dash_html():
    assertions = {
        "Foo - Bar": paragraph("Foo &ndash; Bar"),
        "Foo-Bar": paragraph("Foo-Bar"),
        "$1 - 2$": "\n$$1 - 2$$\n\n",
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlRenderer) == assertions[assertion]


@pytest.mark.latex
def test_dash_latex():
    assertions = {
        "Foo - Bar": "\nFoo -- Bar\n",
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmLaTeXRenderer) == assertions[assertion]
