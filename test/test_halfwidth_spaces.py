import mistletoe
import pytest

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from test.util import paragraph


@pytest.mark.html
def test_halfwidth_space_html():
    input = "Dies ist z.B. ein Test. D.h. hier sollten d.h. Spaces ersetzt worden sein."
    target = "Dies ist z.&#8239;B. ein Test. D.&#8239;h. hier sollten d.&#8239;h. Spaces ersetzt worden sein."

    assert mistletoe.markdown(input, FiftyOhmHtmlRenderer) == paragraph(target)


@pytest.mark.latex
def test_halfwidth_space_latex():
    input = "Dies ist z.B. ein Test. D.h. hier sollten d.h. Spaces ersetzt worden sein."
    target = "\nDies ist z.\,B. ein Test. D.\,h. hier sollten d.\,h. Spaces ersetzt worden sein.\n"

    assert mistletoe.markdown(input, FiftyOhmLaTeXRenderer) == target
