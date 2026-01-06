import pytest
from mistletoe import Document

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer


@pytest.mark.html
def test_formula_html():
    assertions = {
        r"$a \cdot b$": "\n" + r"$$a \cdot b$$" + "\n\n",
        r" $a \cdot b$ ": "\n" + r"$$a \cdot b$$" + "\n\n",
        r"$ a \cdot b $": "\n" + r"$$ a \cdot b $$" + "\n\n",
        r"$a \cdot b$" + "\n" + r"$a \cdot b$": "\n" + r"$$a \cdot b$$" + "\n\n\n" + r"$$a \cdot b$$" + "\n\n",
        r"Lorem Ipsum" + "\n" + r"$a \cdot b$": "<p>Lorem Ipsum</p>\n\n" + r"$$a \cdot b$$" + "\n\n",
    }

    with FiftyOhmHtmlRenderer() as renderer:
        for assertion in assertions:
            assert renderer.render(Document(assertion)) == assertions[assertion]
