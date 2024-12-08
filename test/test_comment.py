import mistletoe
import pytest
from mistletoe.ast_renderer import AstRenderer

from renderer.comment import BlockComment, SpanComment
from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer
from test.util import paragraph


def test_comment_html(capsys) :

    assertions = {
        "%Comment\nBar" : "<p>Bar</p>\n",
        # TODO: This test is not working as expected. The comment should be removed
        #"%Comment\n" : "a",
        "Foo\n%Comment\nBar" : "<p>Foo\nBar</p>\n",
    }

    for assertion in assertions:
        assert mistletoe.markdown(assertion, FiftyOhmHtmlRenderer) == assertions[assertion]
