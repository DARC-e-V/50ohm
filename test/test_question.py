import json

import pytest
from mistletoe import Document

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from test.util import paragraph


@pytest.mark.html
def test_question_html():
    assertions = {
        "[question:123]": "123\n",
        "\n[question:123]\n": "123\n",
        "\n[question:123]\n[question:123]": "123\n123\n",
        "Foo\n[question:123]\nBar": paragraph("Foo") + "123\n" + paragraph("Bar"),
    }

    def test_function(input):
        return f"{input}"

    with FiftyOhmHtmlRenderer(question_renderer=test_function) as renderer:
        for assertion in assertions:
            assert renderer.render(Document(assertion)) == assertions[assertion]

@pytest.mark.html
def test_question_translation_html():
    assertions = {
        "[question:123]": "ED111\n",
        "\n[question:123]\n": "ED111\n",
        "\n[question:123]\n[question:123]": "ED111\nED111\n",
        "Foo\n[question:123]\nBar": paragraph("Foo") + "ED111\n" + paragraph("Bar"),
    }

    def test_function(input):
        with open('data/metadata.json') as file:
            metadata = json.load(file)
        return metadata[f"{input}"].get("number")

    with FiftyOhmHtmlRenderer(question_renderer=test_function) as renderer:
        for assertion in assertions:
            assert renderer.render(Document(assertion)) == assertions[assertion]


@pytest.mark.latex
def test_question_latex():
    assertions = {
        "[question:123]": "\question{123}",
        "\n[question:123]\n": "\question{123}",
        "\n[question:123]\n[question:123]": "\question{123}\question{123}",
        "Foo\n[question:123]\nBar": "\nFoo\n\question{123}\nBar\n",
    }

    def test_function(input):
        return "\\question{"+input+"}"

    with FiftyOhmLaTeXRenderer(test_function) as renderer:
        for assertion in assertions:
            assert renderer.render(Document(assertion)) == assertions[assertion]
