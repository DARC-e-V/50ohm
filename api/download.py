import json

from tqdm import tqdm


class Download:
    def __init__(self, api):
        self.api = api
    
    def download_edition(cls, edition) :
        print("Downloading edition " + edition)

        in_edition = cls.api.get_one(
            "items/edition",
            {"filter": {"ident": {"_eq": edition}}}
        )

        in_chapters = cls.api.get(
            "items/chapter",
            {"filter": {"edition": {"edition_id": {"_eq": in_edition["id"]}}}},
        )

        out_chapters = []

        for in_chapter in tqdm(in_chapters):

            in_sections = cls.api.get(
                "items/section",
                {"filter": {"chapter": {"chapter_id": {"_eq": in_chapter["id"]}}}},
            )

            out_chapters.append(
                {
                    "title": in_chapter["title"],
                    "abstract": in_chapter["abstract"],
                    "sections": [],
                }
            )

            for in_section in in_sections:
                out_chapters[-1]["sections"].append(
                    {
                        "title": in_section["title"],
                        "ident": in_section["ident"],
                        "status": in_section["status"],
                        "content": in_section["content"],
                        "slide": in_section["slide"],
                        "video": in_section["video_url"],
                        "questions": [],
                    }
                )

            with open("data/book_"+edition+".json", "w", encoding="utf-8") as file:
                json.dump(out_chapters, file, ensure_ascii=False, indent=4)

    def download_question_metadata(cls) :
        print("Downloading question metadata")

        questions = cls.api.get(
            "items/questions",
            params={"filter": {"class_3": {"_in": [1,2,3]}}, "sort": "position"}
        )

        result = {}

        for question in questions:
            result[question["id"]] = {
                "number":           question["number"],
                "picture_question": question["picture_question"] if question["picture_question"] is not None else "",
                "picture_a":        question["picture_a"]        if question["picture_a"]        is not None else "",
                "picture_b":        question["picture_b"]        if question["picture_b"]        is not None else "",
                "picture_c":        question["picture_c"]        if question["picture_c"]        is not None else "",
                "picture_d":        question["picture_d"]        if question["picture_d"]        is not None else "",
                "layout":           question["layout"]           if question["layout"]           is not None else "",
            }

        # Serializing json:
        with open("data/metadata.json", "w") as f:
            json.dump(result, f, indent=4)
        f.close()

