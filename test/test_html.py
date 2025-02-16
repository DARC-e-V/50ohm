import json

from mistletoe import Document

from renderer.fifty_ohm_html_renderer import FiftyOhmHtmlRenderer


def question_stub(input):
    with open('data/metadata.json') as file:
        metadata = json.load(file)
    return metadata[f"{input}"].get("number")


def test_html(capsys):
    with capsys.disabled():
        with open("test/acceptanceTest.md") as file:
            content = file.read()
            with FiftyOhmHtmlRenderer(question_stub) as renderer:
                output = renderer.render(Document(content))
                with open("test/acceptanceTest.html", "w") as output_file:
                    output_file.write(output)
