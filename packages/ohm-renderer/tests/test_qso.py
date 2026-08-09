import pytest
from ohm_renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from util import render_html, render_mdx, render_slide


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
        assert render_html(assertion) == assertions[assertion]


@pytest.mark.mdx
def test_qso_mdx():
    # "received" is a JSX expression, not a string, so the frontend gets a real boolean.
    assertions = {
        "<qso>\nfoo\n</qso>": "<Qso>\n<QsoLine received={false}>foo</QsoLine>\n</Qso>\n",
        "<qso>\nfoo\n> bar\n</qso>": (
            "<Qso>\n<QsoLine received={false}>foo</QsoLine>\n<QsoLine received={true}>bar</QsoLine>\n</Qso>\n"
        ),
        "<qso>\n*foo*\n> bar\n</qso>": (
            "<Qso>\n<QsoLine received={false}>*foo*</QsoLine>\n<QsoLine received={true}>bar</QsoLine>\n</Qso>\n"
        ),
        # Blank source lines become QsoLines too, and are dropped again on output.
        "<qso>\nfoo\n\n> bar\n</qso>": (
            "<Qso>\n<QsoLine received={false}>foo</QsoLine>\n<QsoLine received={true}>bar</QsoLine>\n</Qso>\n"
        ),
    }

    for assertion in assertions:
        assert render_mdx(assertion) == assertions[assertion]


@pytest.mark.slide
def test_qso_slide():
    assertions = {
        "<qso>\nfoo\n> bar\n</qso>": '<div class="qso r-fit-text">\n<div class="qso_own fragment fade-right">foo</div>\n<div class="qso_other fragment fade-left">bar</div>\n</div>\n\n',  # noqa: E501
    }

    for assertion in assertions:
        assert render_slide(assertion) == assertions[assertion]
