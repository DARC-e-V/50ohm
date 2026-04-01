import mistletoe
import pytest

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from test.util import paragraph


@pytest.mark.html
def test_index_html():

    assertions = {
        "Im Betrieb werden Yagi-Antennen [index:Antenne:Yagi-Antenne] oft gedreht": "Im Betrieb werden Yagi-Antennen oft gedreht",
        "Im Betrieb werden Yagi-Antennen[index:Antenne:Yagi-Antenne] oft gedreht": "Im Betrieb werden Yagi-Antennen oft gedreht",
        "Im Betrieb werden Yagi-Antennen [index:Antenne] oft gedreht": "Im Betrieb werden Yagi-Antennen oft gedreht",
        "Im Betrieb werden Yagi-Antennen[index:Antenne] oft gedreht": "Im Betrieb werden Yagi-Antennen oft gedreht",
    }

    for key, value in assertions.items():
        assert mistletoe.markdown(key, FiftyOhmHtmlRenderer) == paragraph(value)
