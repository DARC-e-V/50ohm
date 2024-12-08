import mistletoe

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer

def test_thematic_break_html() :
    assertions = {
        "---" : '<a id="margin_1"></a>\n',
        "---\n---" : '<a id="margin_1"></a>\n<a id="margin_2"></a>\n',
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlRenderer) == assertions[assertion]

def test_tag_html() :

    assertions = {
        "<margin>\nFoo\n</margin>" : FiftyOhmHtmlRenderer.render_tag_helper("margin","<p>Foo</p>",1,0)+'\n',
        "<indepth>\nFoo\n</indepth>" : FiftyOhmHtmlRenderer.render_tag_helper("indepth","<p>Foo</p>",1,0)+'\n',
        "<webmargin>\nFoo\n</webmargin>" : FiftyOhmHtmlRenderer.render_tag_helper("margin","<p>Foo</p>",1,0)+'\n',
        "<tipp>\nFoo\n</tipp>" : FiftyOhmHtmlRenderer.render_tag_helper("tipp","<p>Foo</p>",1,0)+'\n',
        "<webtipp>\nFoo\n</webtipp>" : FiftyOhmHtmlRenderer.render_tag_helper("tipp","<p>Foo</p>",1,0)+'\n',
        "<webindepth>\nFoo\n</webindepth>" : FiftyOhmHtmlRenderer.render_tag_helper("indepth","<p>Foo</p>",1,0)+'\n',
        "<unit>\nFoo\n</unit>" : FiftyOhmHtmlRenderer.render_tag_helper("unit","<p>Foo</p>",1,0)+'\n',
        "<danger>\nFoo\n</danger>" : FiftyOhmHtmlRenderer.render_tag_helper("danger","<p>Foo</p>",1,0)+'\n',
        "<webonly>\nFoo\n</webonly>" : '<p>Foo</p>\n',
        "<latexonly>\nFoo\n</latexonly>" : "",
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlRenderer) == assertions[assertion]

def test_thematic_break_and_tag_html() :

    assertions = {
        "---\n<margin>\nFoo\n</margin>" : '<a id="margin_1"></a>\n'+FiftyOhmHtmlRenderer.render_tag_helper("margin","<p>Foo</p>",1,1)+'\n',
        "---\n<margin>\nFoo\n</margin>\n<margin>\nFoo\n</margin>" : '<a id="margin_1"></a>\n'+FiftyOhmHtmlRenderer.render_tag_helper("margin","<p>Foo</p>",1,1)+'\n'+FiftyOhmHtmlRenderer.render_tag_helper("margin","<p>Foo</p>",2,1)+'\n',
        "---\n<margin>\nFoo\n</margin>\n---\n<margin>\nFoo\n</margin>" : '<a id="margin_1"></a>\n'+FiftyOhmHtmlRenderer.render_tag_helper("margin","<p>Foo</p>",1,1)+'\n<a id="margin_2"></a>\n'+FiftyOhmHtmlRenderer.render_tag_helper("margin","<p>Foo</p>",2,2)+'\n',
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlRenderer) == assertions[assertion]