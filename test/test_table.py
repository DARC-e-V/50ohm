import pytest
from mistletoe import Document

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer


@pytest.mark.html
def test_question_html():
    assertions = {
        "| l: abc | r: abc | X: abc |\n| 123 | 456 | 789 | \n | 987 | 654 | 321 | ": "<table><tr><th style='text-align: left;'> abc</th><th style='text-align: right;'> abc</th><th> abc</th></tr><tr><td style='text-align: left;'>123</td><td style='text-align: right;'>456</td><td>789</td></tr><tr><td style='text-align: left;'>987</td><td style='text-align: right;'>654</td><td>321</td></tr></table>\n",
        "text\n| l: abc | r: abc | X: abc |\n| 123 | 456 | 789 | \n | 987 | 654 | 321 |\ntext": "text\n<table><tr><th style='text-align: left;'> abc</th><th style='text-align: right;'> abc</th><th> abc</th></tr><tr><td style='text-align: left;'>123</td><td style='text-align: right;'>456</td><td>789</td></tr><tr><td style='text-align: left;'>987</td><td style='text-align: right;'>654</td><td>321</td></tr></table>\ntext\n",
    }

    def test_function(input):
        return f"{input}"

    with FiftyOhmHtmlRenderer(test_function) as renderer:
        for assertion in assertions:
            assert renderer.render(Document(assertion)) == assertions[assertion]
