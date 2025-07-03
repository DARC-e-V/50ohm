import mistletoe
import pytest

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_html_slide_renderer import FiftyOhmHtmlSlideRenderer


@pytest.mark.html
def test_qso_html():
    assertions = {
        "<qso>\nfoo\n</qso>": FiftyOhmHtmlRenderer.render_tag_helper("qso", '<div class="qso_own">foo</div>\n', 1, 0)
        + "\n",
        "<qso>\nfoo\n> bar\n</qso>": FiftyOhmHtmlRenderer.render_tag_helper(
            "qso", '<div class="qso_own">foo</div>\n<div class="qso_other">bar</div>\n', 1, 0
        )
        + "\n",
        "<qso>\n*foo*\n> bar\n</qso>": FiftyOhmHtmlRenderer.render_tag_helper(
            "qso", '<div class="qso_own"><em>foo</em></div>\n<div class="qso_other">bar</div>\n', 1, 0
        )
        + "\n",
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlRenderer) == assertions[assertion]


@pytest.mark.slide
def test_qso_slide():
    assertions = {
        "<qso>\nfoo\n> bar\n</qso>": '<div class="qso r-fit-text">\n<div class="qso_own fragment fade-right">foo</div>\n<div class="qso_other fragment fade-left">bar</div>\n</div>\n\n',  # noqa: E501
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlSlideRenderer) == assertions[assertion]
