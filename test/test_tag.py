import mistletoe
import pytest

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_html_slide_renderer import FiftyOhmHtmlSlideRenderer
from renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from test.util import paragraph


@pytest.mark.html
def test_thematic_break_html():
    assertions = {
        "---": '<a id="margin_1"></a>\n',
        "---\n---": '<a id="margin_1"></a>\n<a id="margin_2"></a>\n',
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlRenderer) == assertions[assertion]


@pytest.mark.html
def test_tag_html():
    assertions = {
        "<margin>\nFoo\n</margin>": FiftyOhmHtmlRenderer.render_tag_helper("margin", "<p>Foo</p>", 1, 0) + "\n",
        "<indepth>\nFoo\n</indepth>": FiftyOhmHtmlRenderer.render_tag_helper("indepth", "<p>Foo</p>", 1, 0) + "\n",
        "<webmargin>\nFoo\n</webmargin>": FiftyOhmHtmlRenderer.render_tag_helper("margin", "<p>Foo</p>", 1, 0) + "\n",
        "<tip>\nFoo\n</tip>": FiftyOhmHtmlRenderer.render_tag_helper("tip", "<p>Foo</p>", 1, 0) + "\n",
        "<person>\nFoo\n</person>": FiftyOhmHtmlRenderer.render_tag_helper("person", "<p>Foo</p>", 1, 0) + "\n",
        "<webtip>\nFoo\n</webtip>": FiftyOhmHtmlRenderer.render_tag_helper("tip", "<p>Foo</p>", 1, 0) + "\n",
        "<webindepth>\nFoo\n</webindepth>": FiftyOhmHtmlRenderer.render_tag_helper("indepth", "<p>Foo</p>", 1, 0)
        + "\n",
        "<unit>\nFoo\n</unit>": FiftyOhmHtmlRenderer.render_tag_helper("unit", "<p>Foo</p>", 1, 0) + "\n",
        "<danger>\nFoo\n</danger>": FiftyOhmHtmlRenderer.render_tag_helper("danger", "<p>Foo</p>", 1, 0) + "\n",
        "<wordorigin>\nFoo\n</wordorigin>": FiftyOhmHtmlRenderer.render_tag_helper("wordorigin", "<p>Foo</p>", 1, 0)
        + "\n",
        "<webonly>\nFoo\n</webonly>": "<p>Foo</p>\n",
        "<latexonly>\nFoo\n</latexonly>": "",
        "<margin>Foo</margin>": paragraph("<margin>Foo</margin>"),
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlRenderer) == assertions[assertion]


@pytest.mark.html
def test_thematic_break_and_tag_html():
    assertions = {
        "---\n<margin>\nFoo\n</margin>": '<a id="margin_1"></a>\n'
        + FiftyOhmHtmlRenderer.render_tag_helper("margin", "<p>Foo</p>", 1, 1)
        + "\n",
        "---\n<margin>\nFoo\n</margin>\n<margin>\nFoo\n</margin>": '<a id="margin_1"></a>\n'
        + FiftyOhmHtmlRenderer.render_tag_helper("margin", "<p>Foo</p>", 1, 1)
        + "\n"
        + FiftyOhmHtmlRenderer.render_tag_helper("margin", "<p>Foo</p>", 2, 1)
        + "\n",
        "---\n<margin>\nFoo\n</margin>\n---\n<margin>\nFoo\n</margin>": '<a id="margin_1"></a>\n'
        + FiftyOhmHtmlRenderer.render_tag_helper("margin", "<p>Foo</p>", 1, 1)
        + '\n<a id="margin_2"></a>\n'
        + FiftyOhmHtmlRenderer.render_tag_helper("margin", "<p>Foo</p>", 2, 2)
        + "\n",
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlRenderer) == assertions[assertion]


@pytest.mark.latex
def test_thematic_break_latex():
    assertions = {
        "---": "",
        "---\n---": "",
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmLaTeXRenderer) == assertions[assertion]


@pytest.mark.latex
def test_tag_latex():
    assertions = {
        "<margin>\nFoo\n</margin>": "\\Margin{\nFoo\n}",
        "<danger>\nFoo\n</danger>": "\\MarginDanger{\nFoo\n}",
        "<warning>\nFoo\n</warning>": "\\MarginWarning{\nFoo\n}",
        "<attention>\nFoo\n</attention>": "\\MarginAttention{\nFoo\n}",
        "<tip>\nFoo\n</tip>": "\\MarginTip{\nFoo\n}",
        "<webtip>\nFoo\n</webtip>": "\\WebTip{\nFoo\n}",
        "<unit>\nFoo\n</unit>": "\\MarginUnit{\nFoo\n}",
        "<indepth>\nFoo\n</indepth>": "\\MarginInDepth{\nFoo\n}",
        "<webindepth>\nFoo\n</webindepth>": "\\MarginWebInDepth{\nFoo\n}",
        "<webmargin>\nFoo\n</webmargin>": "\\WebMargin{\nFoo\n}",
        "<fullwidth>\nFoo\n</fullwidth>": "\\FullWidth{\nFoo\n}",
        "<latexonly>\nFoo\n</latexonly>": "\nFoo\n",
        "<webonly>\nFoo\n</webonly>": "",
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmLaTeXRenderer) == assertions[assertion]


@pytest.mark.latex
def test_thematic_break_and_tag_latex():
    assertions = {
        "---\n<margin>\nFoo\n</margin>": "\\Margin{\nFoo\n}",
        "---\n<margin>\nFoo\n</margin>\n<margin>\nFoo\n</margin>": "\\Margin{\nFoo\n}\\Margin{\nFoo\n}",
        "---\n<margin>\nFoo\n</margin>\n---\n<margin>\nFoo\n</margin>": "\\Margin{\nFoo\n}\\Margin{\nFoo\n}",
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmLaTeXRenderer) == assertions[assertion]


@pytest.mark.slide
def test_tag_slide():
    assertions = {
        "<note>\nFoo\n</note>": '<aside class="notes">\n<p>Foo</p>\n</aside>\n\n',
        "<fragment>\nFoo\n</fragment>": '<div class="fragment">\n<p>Foo</p>\n</div>\n\n',
        "<left>\nFoo\n</left>": '<div id="left">\n<p>Foo</p>\n</div>\n\n',
        "<right>\nFoo\n</right>": '<div id="right">\n<p>Foo</p>\n</div>\n\n',
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlSlideRenderer) == assertions[assertion]


@pytest.mark.slide
def test_slide_break():
    assertions = {
        "---\na\n": "<section>\n<p>a</p>\n</section>\n\n",
        "---\na\n---\nb\n": "<section>\n<p>a</p>\n</section>\n\n<section>\n<p>b</p>\n</section>\n\n",
        "--- foo\na\n": "<section foo>\n<p>a</p>\n</section>\n\n",
        "--- foo bar\na\n": "<section foo bar>\n<p>a</p>\n</section>\n\n",
        "---   foo bar  \na\n": "<section foo bar>\n<p>a</p>\n</section>\n\n",
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlSlideRenderer) == assertions[assertion]
