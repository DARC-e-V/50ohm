import mistletoe
import pytest
from ohm_renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from util import paragraph, render_html, render_mdx


@pytest.mark.html
def test_dash_html():
    assertions = {
        "Foo - Bar": "Foo &ndash; Bar",
        "Foo-Bar": "Foo-Bar",
    }

    for assertion in assertions:
        assert render_html(assertion) == paragraph(assertions[assertion])


@pytest.mark.mdx
def test_dash_mdx():
    # Two hyphens on purpose, the MDX pipeline turns them into an en dash.
    assertions = {
        "Foo - Bar": "Foo -- Bar\n",
        "Foo-Bar": "Foo-Bar\n",
    }

    for assertion in assertions:
        assert render_mdx(assertion) == assertions[assertion]


@pytest.mark.latex
def test_dash_latex():
    assertions = {
        "Foo - Bar": "\nFoo -- Bar\n",
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmLaTeXRenderer) == assertions[assertion]
