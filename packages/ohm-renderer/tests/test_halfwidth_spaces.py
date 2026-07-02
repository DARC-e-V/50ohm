import mistletoe
import pytest
from ohm_renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from util import paragraph, render_html


@pytest.mark.html
def test_halfwidth_space_html():
    input = "Dies ist z.B. ein Test. D.h. hier sollten d.h. Spaces ersetzt worden sein."
    target = "Dies ist z.&#8239;B. ein Test. D.&#8239;h. hier sollten d.&#8239;h. Spaces ersetzt worden sein."

    assert render_html(input) == paragraph(target)


@pytest.mark.latex
def test_halfwidth_space_latex():
    input = "Dies ist z.B. ein Test. D.h. hier sollten d.h. Spaces ersetzt worden sein."
    target = "\nDies ist z.\\,B. ein Test. D.\\,h. hier sollten d.\\,h. Spaces ersetzt worden sein.\n"

    assert mistletoe.markdown(input, FiftyOhmLaTeXRenderer) == target
