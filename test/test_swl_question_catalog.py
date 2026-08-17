import json

from src.build import Build
from src.config import Config


def write_catalog(path, number):
    path.write_text(
        json.dumps(
            {
                "sections": [
                    {
                        "title": f"Katalog {number}",
                        "questions": [
                            {
                                "number": number,
                                "class": "SWL" if number.startswith("SWL") else "1",
                                "question": f"Frage {number}",
                                "answer_a": "A",
                                "answer_b": "B",
                                "answer_c": "C",
                                "answer_d": "D",
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )


def prepare_content(tmp_path, include_swl):
    questions_path = tmp_path / "contents" / "questions"
    questions_path.mkdir(parents=True)
    write_catalog(questions_path / "fragenkatalog3b.json", "NA101")
    (questions_path / "metadata3b.json").write_text(
        json.dumps(
            {
                "NA101": {
                    "directus_id": "1",
                    "picture_question": "",
                    "picture_a": "",
                    "picture_b": "",
                    "picture_c": "",
                    "picture_d": "",
                    "layout": "",
                }
            }
        ),
        encoding="utf-8",
    )
    if include_swl:
        write_catalog(questions_path / "fragenkatalog_swl.json", "SWL001")


def test_optional_swl_catalog_is_loaded_with_default_metadata(tmp_path):
    prepare_content(tmp_path, include_swl=True)

    build = Build(Config(content_path=tmp_path, build_path=tmp_path / "build"))

    assert set(build.questions) == {"NA101", "SWL001"}
    assert build.question_metadata["SWL001"]["layout"] == ""
    assert len(build.fragenkatalog["sections"]) == 2


def test_missing_optional_swl_catalog_is_allowed(tmp_path):
    prepare_content(tmp_path, include_swl=False)

    build = Build(Config(content_path=tmp_path, build_path=tmp_path / "build"))

    assert set(build.questions) == {"NA101"}
    assert len(build.fragenkatalog["sections"]) == 1
