import mistletoe

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from test.util import paragraph

def test_halfwidth_space_html():
    input = "Dies ist z.B. ein Test. D.h. hier sollten d.h. Spaces ersetzt worden sein."
    target = "Dies ist z.&#8239;B. ein Test. D.&#8239;h. hier sollten d.&#8239;h. Spaces ersetzt worden sein."

    assert mistletoe.markdown(input, FiftyOhmHtmlRenderer) == paragraph(target)
