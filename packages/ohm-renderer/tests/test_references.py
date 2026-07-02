import pytest
from util import paragraph, render_html


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
