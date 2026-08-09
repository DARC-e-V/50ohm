import pytest
from ohm_renderer.document import Document
from ohm_renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from util import render_mdx


@pytest.mark.html
def test_include_html():
    assertions = {
        "[include:ident]": "ident\n",
    }

    def test_function(input):
        return f"{input}"

    with FiftyOhmHtmlRenderer(include_handler=test_function) as renderer:
        for assertion in assertions:
            assert renderer.render(Document(assertion)) == assertions[assertion]


@pytest.mark.mdx
def test_include_mdx():
    # Raw HTML with a <script> would break MDX, so the include stays a component call.
    assertions = {
        "[include:ident]": '<Include ident="ident" />\n',
        "[include:a]\n[include:b]": '<Include ident="a" />\n<Include ident="b" />\n',
    }

    for assertion in assertions:
        assert render_mdx(assertion) == assertions[assertion]
