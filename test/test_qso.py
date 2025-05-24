import mistletoe
import pytest

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer


@pytest.mark.html
def test_table_html():
    assertions = {
        "<qso>\nfoo\n</qso>": FiftyOhmHtmlRenderer.render_tag_helper("qso", '<div class="qso_own">foo</div>', 1, 0) +"\n", 
        "<qso>\nfoo\n> bar\n</qso>": FiftyOhmHtmlRenderer.render_tag_helper("qso", '<div class="qso_own">foo</div><div class="qso_other">bar</div>', 1, 0) +"\n", 
        "<qso>\n*foo*\n> bar\n</qso>": FiftyOhmHtmlRenderer.render_tag_helper("qso", '<div class="qso_own"><em>foo</em></div><div class="qso_other">bar</div>', 1, 0) +"\n", 
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlRenderer) == assertions[assertion]

