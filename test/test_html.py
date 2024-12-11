import mistletoe

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer


def test_html(capsys):
    with capsys.disabled():
        with open("test/acceptanceTest.md") as file:
            content = file.read()
            output = mistletoe.markdown(content, FiftyOhmHtmlRenderer)
            with open("test/acceptanceTest.html", "w") as output_file:
                output_file.write(output)
