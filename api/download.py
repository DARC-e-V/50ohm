import json
import multiprocessing
import os

from joblib import Memory, Parallel, delayed
from tqdm import tqdm


class Download:
    def __init__(self, api):
        self.api = api
    
    def download_edition(self, edition) :

        in_edition = self.api.get_one(
            "items/edition",
            {"filter": {"ident": {"_eq": edition}}}
        )

        in_chapters = self.api.get(
            "items/chapter",
            {"filter": {"edition": {"edition_id": {"_eq": in_edition["id"]}}}},
        )

        out_chapters = []

        for in_chapter in tqdm(in_chapters,  desc="Downloading edition"):

            in_sections = self.api.get(
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

    def download_question_metadata(self) :

        questions = self.api.get(
            "items/questions",
            params={"filter": {"class_3": {"_in": [1,2,3]}}, "sort": "position"}
        )

        result = {}

        for question in tqdm(questions, desc="Downloading question metadata"):
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

    def download_photos(self) :

        photos = self.api.get(
            "items/Fotos",
            params={ "limit": -1 }
        )

        for photo in tqdm(photos, desc="Downloading photos"):
            data = self.api.get_file("assets/" + photo["photo"])
            file = open("./data/photos/" + str(photo["id"]) + ".jpg", "wb")
            file.write(data)
            file.close()

    def __symlink_pictures(self) :
        os.chdir("./data/pictures")
        if not os.path.islink("foto"):
            os.system("ln -s ../photos foto")
        os.chdir("../..")

    def download_pictures(self) :
        self.__symlink_pictures()
        
        memory=Memory("./cache", verbose=0)

        @memory.cache
        def build_picture(picture) :
            pid = picture["id"]
            
            if "\\begin{document}" in picture["latex"] or "\\begin{table}" in picture["latex"]: # Workaround, if the picture contains a document class it should be ignored!
                return
            
            with open(f"./data/pictures/{pid}.tex", 'w', encoding='utf-8') as file:
                # Write the auxilary LaTeX file:
                file.write(f"\\documentclass{{BNetzA-Fragenkatalog}}\\DARCimageOnly{{9cm}}{{{picture['id']}include}}")
                file.close()
                # Build the picture:
                os.system(f"latexmk -lualatex -f -interaction=nonstopmode ./data/pictures/{pid}.tex > /dev/null 2>&1")
                # Convert the PDF to SVG:
                os.system(f"pdftocairo -svg data/pictures/{picture['id']}.pdf - > data/pictures/{picture['id']}.svg > /dev/null 2>&1")
                # Remove all build files:
                #os.system(f"latexmk -C ./data/pictures/{pid}.tex > /dev/null 2>&1")
                #os.system(f"rm ./data/pictures/{pid}.tex > /dev/null 2>&1")

        pictures = self.api.get(
            "items/pictures",
            params={ "limit": -1 }
        )

        for picture in tqdm(pictures, desc="Download all pictures"):
            latex = picture["latex"]
            with open("./data/pictures/img/" + str(picture["id"]) + "include.tex", "w") as file:
                file.write(latex)
            file.close()

        #for picture in tqdm(pictures, desc="Build all pictures"):
        #    build_picture(picture)
        Parallel(n_jobs=multiprocessing.cpu_count())(
            delayed(build_picture)(picture) for picture in tqdm(pictures, desc="Build All Pictures")
        )


                