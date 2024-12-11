import mistletoe
import pytest

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from test.util import paragraph


@pytest.mark.html
def test_references_html():
    # Right now this tests only the default values.
    # The correct behavior can be tested when the information is added to the renderer class
    assertions = {
        "[ref:e_oszilloskop_bildschirmfoto_sinus]": '<a href="section.html#ref_e_oszilloskop_bildschirmfoto_sinus" onclick="highlightRef(\'e_oszilloskop_bildschirmfoto_sinus\');">0</a>',
        "[ref:n_rst_r]": '<a href="section.html#ref_n_rst_r" onclick="highlightRef(\'n_rst_r\');">0</a>',
        "[ref:Uuuuuh]": '<a href="section.html#ref_Uuuuuh" onclick="highlightRef(\'Uuuuuh\');">0</a>',  # Test the default parameters
    }

    for key, value in assertions.items():
        assert mistletoe.markdown(key, FiftyOhmHtmlRenderer) == paragraph(value)
