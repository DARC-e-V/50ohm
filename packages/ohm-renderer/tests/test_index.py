import mistletoe
import pytest
from ohm_renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from util import paragraph, render_html, render_mdx


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
        assert render_html(key) == paragraph(value)


@pytest.mark.mdx
def test_index_mdx():
    assertions = {
        "Im Betrieb werden Yagi-Antennen [index:Antenne:Yagi-Antenne] oft gedreht": (
            'Im Betrieb werden Yagi-Antennen<Index first="Antenne" second="Yagi-Antenne" /> oft gedreht\n'
        ),
        "Im Betrieb werden Yagi-Antennen[index:Antenne] oft gedreht": (
            'Im Betrieb werden Yagi-Antennen<Index first="Antenne" /> oft gedreht\n'
        ),
        "Im Betrieb werden Yagi-Antennen[index:Test Antenne] oft gedreht": (
            'Im Betrieb werden Yagi-Antennen<Index first="Test Antenne" /> oft gedreht\n'
        ),
        # Each anchor is emitted only once per document.
        "Im Betrieb [index:Antenne] und nochmals [index:Antenne] oft gedreht": (
            'Im Betrieb<Index first="Antenne" /> und nochmals oft gedreht\n'
        ),
    }

    for key, value in assertions.items():
        assert render_mdx(key) == value


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
