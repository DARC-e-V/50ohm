import pytest
from mistletoe import Document

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from test.util import paragraph


@pytest.mark.html
def test_comment_html():
    assertions = {
        "[question:123]": "123\n",
        "\n[question:123]\n": "123\n",
        "\n[question:123]\n[question:123]": "123\n123\n",
        "Foo\n[question:123]\nBar": paragraph("Foo") + "123\n" + paragraph("Bar"),
    }

    def test_function(input):
        return f"{input}"

    with FiftyOhmHtmlRenderer(test_function) as renderer:
        for assertion in assertions:
            assert renderer.render(Document(assertion)) == assertions[assertion]


@pytest.mark.latex
def test_comment_latex():
    assertions = {
        "[question:123]": "123",
        "\n[question:123]\n": "123",
        "\n[question:123]\n[question:123]": "123123",
        "Foo\n[question:123]\nBar": "\nFoo\n123\nBar\n",
    }

    def test_function(input):
        return f"{input}"

    with FiftyOhmLaTeXRenderer(test_function) as renderer:
        for assertion in assertions:
            assert renderer.render(Document(assertion)) == assertions[assertion]
