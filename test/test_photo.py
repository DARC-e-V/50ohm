import mistletoe
import pytest

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from renderer.fifty_ohm_latex_renderer import FiftyOhmLaTeXRenderer
from test.util import paragraph


@pytest.mark.html
def test_photo_html():
    # Test with edition context
    assertions_with_context = {
        "[photo:123:abc:Text]": FiftyOhmHtmlRenderer.render_photo_helper("123", "abc", "Text", "N-2.3.1"),
    }

    for assertion in assertions_with_context:
        with FiftyOhmHtmlRenderer(edition="N", chapter_number=2, section_number=3) as renderer:
            from mistletoe import Document

            result = renderer.render(Document(assertion))
            assert result == paragraph(assertions_with_context[assertion])

    # Test without context (fallback to simple numbering)
    assertions_no_context = {
        "[photo:123:abc:Text]": FiftyOhmHtmlRenderer.render_photo_helper("123", "abc", "Text", "1"),
    }

    for assertion in assertions_no_context:
        with FiftyOhmHtmlRenderer() as renderer:
            from mistletoe import Document

            result = renderer.render(Document(assertion))
            assert result == paragraph(assertions_no_context[assertion])


@pytest.mark.latex
def test_photo_latex():
    assertions = {
        "[photo:123:abc:Text]": FiftyOhmLaTeXRenderer.render_photo_helper("123", "abc", "Text", "TODO"),
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmLaTeXRenderer) == "\n" + assertions[assertion] + "\n"
