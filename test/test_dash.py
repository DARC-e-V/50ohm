import mistletoe
import pytest

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from test.util import paragraph


@pytest.mark.html
def test_dash_html():
    assertions = {
        "Foo - Bar": "Foo &ndash; Ba",
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlRenderer) == paragraph(assertions[assertion])


@pytest.mark.latex
def test_dash_latex():
    assertions = {
        "Foo - Bar": "\nFoo -- Bar\n",
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmLaTeXRenderer) == assertions[assertion]
