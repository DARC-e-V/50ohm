import json
import multiprocessing
import os
import shutil

from joblib import Memory, Parallel, delayed
from tqdm import tqdm

from api.directus import DirectusAPI

from .config import Config


class Download:
    def __init__(self, api: DirectusAPI, content_api: DirectusAPI, config: Config):
        self.api = api
        self.config = config
        self.content_api = content_api

    def download_edition(self, edition):
        in_edition = self.api.get_one("items/edition", {"filter": {"ident": {"_eq": edition}}})

        in_chapters = self.api.get(
            "items/chapter",
            {"filter": {"edition": {"edition_id": {"_eq": in_edition["id"]}}}},
        )

        out_chapters = []

        for in_chapter in tqdm(in_chapters, desc="Downloading edition"):
            in_sections = self.api.get(
                "items/section",
                {"filter": {"chapter": {"chapter_id": {"_eq": in_chapter["id"]}}}},
            )

            out_chapters.append(
                {
                    "title": in_chapter["title"],
                    "abstract": in_chapter["abstract"],
                    "ident": in_chapter["ident"],
                    "video_url": in_chapter["video_url"],
                    "sections": [],
                }
            )

            for in_section in in_sections:
                out_chapters[-1]["sections"].append(
                    {
                        "title": in_section["title"],
                        "ident": in_section["ident"],
                        "status": in_section["status"],
                        "class": in_section["class"],
                        "content": in_section["content"],
                        "slide": in_section["slide"],
                        "video_url": in_section["video_url"],
                        "questions": [],
                    }
                )

            out_edition = {
                "title": in_edition["title"],
                "abstract": in_edition["abstract"],
                "chapters": out_chapters,
                "edition": edition,
            }

            with (self.config.p_data / f"book_{edition}.json").open("w", encoding="utf-8") as file:
                json.dump(out_edition, file, ensure_ascii=False, indent=4)

    def download_question_metadata(self):
        questions = self.api.get(
            "items/questions", params={"filter": {"class_3": {"_in": [1, 2, 3]}}, "sort": "position", "limit": -1}
        )

        result = {}

        for question in tqdm(questions, desc="Downloading metadata"):
            result[question["id"]] = {
                "number": question["number"],
                "picture_question": question["picture_question"] if question["picture_question"] is not None else "",
                "picture_a": question["picture_a"] if question["picture_a"] is not None else "",
                "picture_b": question["picture_b"] if question["picture_b"] is not None else "",
                "picture_c": question["picture_c"] if question["picture_c"] is not None else "",
                "picture_d": question["picture_d"] if question["picture_d"] is not None else "",
                "layout": question["layout"] if question["layout"] is not None else "",
            }

        # Serializing json:
        with (self.config.p_data / "metadata.json").open("w", encoding="utf-8") as f:
            json.dump(result, f, indent=4)
        f.close()

    def download_photos(self):
        self.config.p_data_photos.mkdir(parents=True, exist_ok=True)

        photos = self.api.get("items/Fotos", params={"limit": -1})

        for photo in tqdm(photos, desc="Downloading photos"):
            data = self.api.get_file("assets/" + photo["photo"])
            with (self.config.p_data_photos / f"{photo['id']}.jpg").open("wb") as file:
                file.write(data)

    def download_pictures(self):
        self.config.p_data_pictures.mkdir(parents=True, exist_ok=True)
        # Symlink photos, so LaTeX can access these assets to render into graphics.
        foto_link = self.config.p_data_pictures / "foto"
        if not foto_link.is_symlink():
            foto_link.symlink_to(self.config.p_data_photos)

        memory = Memory("./cache", verbose=0)

        @memory.cache
        def build_picture(picture):
            pid = picture["id"]

            if (
                "\\begin{document}" in picture["latex"] or "\\begin{table}" in picture["latex"]
            ):  # Workaround, if the picture contains a document class it should be ignored!
                return

            if self.config.no_latex:
                shutil.copyfile("./assets/images/50ohm_gray.svg", self.config.p_data_pictures / f"{pid}.svg")
            else:
                with (self.config.p_data_pictures / f"img/{pid}include.tex").open("w") as file:
                    file.write(picture["latex"])

                aux_file = self.config.p_data_pictures / f"{pid}.tex"
                with aux_file.open("w", encoding="utf-8") as file:
                    # Write the auxilary LaTeX file:
                    file.write(f"\\documentclass{{BNetzA-Fragenkatalog}}\\DARCimageOnly{{9cm}}{{{pid}include}}")
                # Build the picture:
                os.system(f"latexmk -lualatex -f -interaction=nonstopmode {aux_file} > /dev/null 2>&1")
                # Convert the PDF to SVG:
                os.system(
                    "pdftocairo -svg"
                    f"{self.config.p_data_pictures / f'{pid}.pdf'} - > {self.config.p_data_pictures / f'{pid}.svg'}"
                )

        pictures = self.api.get("items/pictures", params={"limit": -1})

        Parallel(n_jobs=multiprocessing.cpu_count())(
            delayed(build_picture)(picture) for picture in tqdm(pictures, desc="Build All Pictures")
        )

    def download_includes(self):
        includes = self.api.get("items/include", params={"limit": -1})

        result = {}
        for include in tqdm(includes, desc="Downloading includes"):
            result[include["ident"]] = include["content"]

            with (self.config.p_data / "includes.json").open("w", encoding="utf-8") as file:
                json.dump(result, file, indent=4)

    def download_snippets(self):
        snippets = {}
        for snippet in tqdm(self.content_api.get("items/snippet"), desc="Downloading snippets"):
            snippets[snippet["ident"]] = snippet["content"]
        with (self.config.p_data / "snippets.json").open("w", encoding="utf-8") as file:
            json.dump(snippets, file, ensure_ascii=False, indent=4)

    def download_content(self):
        contents = []
        for content in tqdm(self.content_api.get("items/content"), desc="Downloading content"):
            contents.append(
                {
                    "url_part": content["url_part"],
                    "content": content["content"],
                    "sidebar": content["sidebar"],
                }
            )

        with (self.config.p_data / "content.json").open("w", encoding="utf-8") as file:
            json.dump(contents, file, ensure_ascii=False, indent=4)
