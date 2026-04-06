import mistletoe
import pytest

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from test.util import paragraph


@pytest.mark.html
def test_index_html():
    assertions = {
        "Im Betrieb werden Yagi-Antennen [index:Antenne:Yagi-Antenne] oft gedreht": (
            "Im Betrieb werden Yagi-Antennen"
            + '<span id="index_antenne__yagi_antenne" class="index-anchor" aria-hidden="true"></span>'
            + " oft gedreht"
        ),
        "Im Betrieb werden Yagi-Antennen[index:Antenne:Yagi-Antenne] oft gedreht": (
            "Im Betrieb werden Yagi-Antennen"
            + '<span id="index_antenne__yagi_antenne" class="index-anchor" aria-hidden="true"></span>'
            + " oft gedreht"
        ),
        "Im Betrieb werden Yagi-Antennen [index:Antenne] oft gedreht": (
            "Im Betrieb werden Yagi-Antennen"
            + '<span id="index_antenne" class="index-anchor" aria-hidden="true"></span>'
            + " oft gedreht"
        ),
        "Im Betrieb werden Yagi-Antennen[index:Antenne] oft gedreht": (
            "Im Betrieb werden Yagi-Antennen"
            + '<span id="index_antenne" class="index-anchor" aria-hidden="true"></span>'
            + " oft gedreht"
        ),
        "Im Betrieb werden Yagi-Antennen[index:Test Antenne] oft gedreht": (
            "Im Betrieb werden Yagi-Antennen"
            + '<span id="index_test_antenne" class="index-anchor" aria-hidden="true"></span>'
            + " oft gedreht"
        ),
        "Im Betrieb [index:Antenne] und nochmals [index:Antenne] oft gedreht": (
            "Im Betrieb"
            + '<span id="index_antenne" class="index-anchor" aria-hidden="true"></span>'
            + " und nochmals oft gedreht"
        ),
    }

    for key, value in assertions.items():
        assert mistletoe.markdown(key, FiftyOhmHtmlRenderer) == paragraph(value)


@pytest.mark.latex
def test_index_latex():
    assertions = {
        "Im Betrieb werden Yagi-Antennen [index:Antenne:Yagi-Antenne] oft gedreht": "Im Betrieb werden Yagi-Antennen\\index{Antenne!Yagi-Antenne} oft gedreht",  # noqa: E501
        "Im Betrieb werden Yagi-Antennen[index:Antenne:Yagi-Antenne] oft gedreht": "Im Betrieb werden Yagi-Antennen\\index{Antenne!Yagi-Antenne} oft gedreht",  # noqa: E501
        "Im Betrieb werden Yagi-Antennen [index:Antenne] oft gedreht": "Im Betrieb werden Yagi-Antennen\\index{Antenne} oft gedreht",  # noqa: E501
        "Im Betrieb werden Yagi-Antennen[index:Antenne] oft gedreht": "Im Betrieb werden Yagi-Antennen\\index{Antenne} oft gedreht",  # noqa: E501
        "Im Betrieb werden Yagi-Antennen [index:Test Antenne] oft gedreht": "Im Betrieb werden Yagi-Antennen\\index{Test Antenne} oft gedreht",  # noqa: E501
    }

    for key, value in assertions.items():
        assert mistletoe.markdown(key, FiftyOhmLaTeXRenderer) == "\n" + value + "\n"
