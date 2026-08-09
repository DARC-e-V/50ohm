import pytest
from util import paragraph, render_html, render_mdx


@pytest.mark.html
def test_references_html():
    # References without figures in the map should show "?"
    assertions = {
        "[ref:e_oszilloskop_bildschirmfoto_sinus]": '<a href="section.html#ref_e_oszilloskop_bildschirmfoto_sinus" onclick="highlightRef(\'e_oszilloskop_bildschirmfoto_sinus\');">?</a>',  # noqa: E501
        "[ref:n_rst_r]": '<a href="section.html#ref_n_rst_r" onclick="highlightRef(\'n_rst_r\');">?</a>',
        "[ref:Uuuuuh]": '<a href="section.html#ref_Uuuuuh" onclick="highlightRef(\'Uuuuuh\');">?</a>',
    }

    for key, value in assertions.items():
        assert render_html(key) == paragraph(value)


@pytest.mark.mdx
def test_references_mdx():
    # References without figures in the map should show "?"
    assertions = {
        "[ref:n_rst_r]": '<Reference marker="n_rst_r" label="?" />\n',
        "[ref:Uuuuuh]": '<Reference marker="Uuuuuh" label="?" />\n',
    }

    for key, value in assertions.items():
        assert render_mdx(key) == value


@pytest.mark.mdx
def test_reference_to_figure_mdx():
    source = "[picture:0:abc:Text]\n\nsiehe [ref:abc]"

    assert render_mdx(source, edition="A", chapter="5", section="7").endswith(
        'siehe <Reference marker="abc" label="A-5.7.1" />\n'
    )
