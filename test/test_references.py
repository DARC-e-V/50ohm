import mistletoe

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from test.util import paragraph

def test_references_html():
    # Right now this tests only the default values. 
    # The correct behavior can be tested when the information is added to the renderer class
    assertions = {
        "[ref:e_oszilloskop_bildschirmfoto_sinus]" : "<a href=&#34;DeineMama.html#ref_e_oszilloskop_bildschirmfoto_sinus&#34; onclick=&#34;highlightRef(&#39;e_oszilloskop_bildschirmfoto_sinus&#39;);&#34;>0</a>",
        "[ref:n_rst_r]" : "<a href=&#34;DeineMama.html#ref_n_rst_r&#34; onclick=&#34;highlightRef(&#39;n_rst_r&#39;);&#34;>0</a>",
        "[ref:Uuuuuh]" : "<a href=&#34;DeineMama.html#ref_Uuuuuh&#34; onclick=&#34;highlightRef(&#39;Uuuuuh&#39;);&#34;>0</a>" # Test the default parameters
    }

    for key, value in assertions.items():
        assert mistletoe.markdown(key, FiftyOhmHtmlRenderer) == paragraph(value)
