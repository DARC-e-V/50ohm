import pytest
from mistletoe import Document

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer


@pytest.mark.html
def test_include_html():
    assertions = {
        '[include:ident]': "ident\n",
    }

    def test_function(input):
        return f"{input}"

    with FiftyOhmHtmlRenderer(include_handler=test_function) as renderer:
        for assertion in assertions:
            assert renderer.render(Document(assertion)) == assertions[assertion]
