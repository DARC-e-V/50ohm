import json
import random

from jinja2 import Environment, FileSystemLoader

from renderer.fifty_ohm_html_slide_renderer import FiftyOhmHtmlSlideRenderer


def parse_katalog():
    with open("data/fragenkatalog3b.json") as fragenkatalog_file:
        fragenkatalog = json.load(fragenkatalog_file)

        questions = {}

        for exampart in fragenkatalog["sections"]:
            for chapter in exampart["sections"]:
                if "questions" in chapter:
                    for question in chapter["questions"]:
                        questions[question["number"]] = question
                if "sections" in chapter:
                    for section in chapter["sections"]:
                        for question in section["questions"]:
                            questions[question["number"]] = question

        return questions

def filter_shuffle_answers(seq):
    try:
        answers = []
        firstrun = True
        for answer in seq:
            if firstrun:
                answers.append({"content": answer, "correct": True})
                firstrun = False
            else:
                answers.append({"content": answer, "correct": False})
        random.shuffle(answers)
        return answers
    except Exception:
        return seq


env = Environment(loader=FileSystemLoader("templates/"))
env.filters["shuffle_answers"] = filter_shuffle_answers
question_template = env.get_template("slide/question.html")
questions = parse_katalog()


def question_stub(input):
    """Combines the original question dataset from BNetzA with our internal metadata"""
    with open("data/metadata.json") as metadata_file:
        metadata = json.load(metadata_file)
        number = metadata[f"{input}"]["number"]  # Fragennummer z.B. AB123

        question = questions[number]
        metadata = metadata[f"{input}"]

        if "answer_a" in question:
            answers = [question["answer_a"], question["answer_b"], question["answer_c"], question["answer_d"]]
        else:
            answers = []

        if metadata["picture_a"] != "":
            answer_pictures = [
                metadata["picture_a"],
                metadata["picture_b"],
                metadata["picture_c"],
                metadata["picture_d"],
            ]
        else:
            answer_pictures = []

        if "picture_question" in question:
            picture_question = metadata["picture_question"]
        else:
            picture_question = ""

        return question_template.render(
            question=question["question"],
            number=number,
            layout=metadata["layout"],
            picture_question=picture_question,
            answers=answers,
            answer_pictures=answer_pictures,
        )


def print_head():
    return """<html><head>
    <meta charset="utf-8">

    <title>DARC Ausbildungsplattform</title>

    <meta name="description" content="">
    <meta name="author" content="">

    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">

    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <link rel="stylesheet" href="../assets/reveal.js/dist/reset.css">
    <link rel="stylesheet" href="../assets/reveal.js/dist/reveal.css">
    <link rel="stylesheet" href="../assets/style-slide.css">

    <!-- Theme used for syntax highlighting of code -->
    <link rel="stylesheet" href="../assets/reveal.js/plugin/highlight/monokai.css">
</head>
<body>
    <div class="reveal">
      <div class="slides">
"""

    #<!-- Chart plugin -->
    #<script src="../assets/reveal.js-plugins/chart/plugin.js"></script>
    #<script src="../assets/chartjs/4.4.1/chart.min.js"></script>

def print_tail():
    return """</div>
    </div>
        <script src="../assets/reveal.js/dist/reveal.js"></script>
        <script src="../assets/reveal.js/plugin/zoom/zoom.js"></script>
        <script src="../assets/reveal.js/plugin/notes/notes.js"></script>
        <script src="../assets/reveal.js/plugin/search/search.js"></script>
        <script src="../assets/reveal.js/plugin/markdown/markdown.js"></script>
        <script src="../assets/reveal.js/plugin/highlight/highlight.js"></script>
        <script src="../assets/reveal.js/plugin/math/math.js"></script>
		<script>

			// Also available as an ES module, see:
			// https://revealjs.com/initialization/
			Reveal.initialize({
				controls: true,
				progress: true,
				slideNumber: 'c/t',
				showSlideNumber: 'speaker',
				center: true,
				hash: true,
				transition: 'slide',
				showNotes: false,
				pdfSeparateFragments: false,

				// Learn about plugins: https://revealjs.com/plugins/
				plugins: [ RevealZoom, RevealNotes, RevealSearch, RevealMarkdown, RevealHighlight, RevealMath.KaTeX] //, RevealChart ]
			});

		</script>
    </body>"""

def test_html_slides(capsys):
    with capsys.disabled():
        with open("test/acceptanceTestSlides.md") as file:
            content = file.read()
            with FiftyOhmHtmlSlideRenderer(question_stub) as renderer:
                output = ""
                output = print_head()
                output += renderer.render_wrapper(content)
                output += print_tail()
                with open("test/acceptanceTestSlides.html", "w") as output_file:
                    output_file.write(output)
