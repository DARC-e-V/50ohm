import json

from git import Repo
from tqdm import tqdm

from api.directus import DirectusAPI

from .config import Config


class Download:
    def __init__(self, content_api: DirectusAPI, config: Config):
        self.config = config
        self.content_api = content_api

    def download_snippets(self):
        snippets = {}
        for snippet in tqdm(self.content_api.get("items/snippet"), desc="Downloading snippets"):
            snippets[snippet["ident"]] = snippet["content"]
        with (self.config.p_data / "snippets.json").open("w", encoding="utf-8") as file:
            json.dump(snippets, file, ensure_ascii=False, indent=4)

    def download_content(self):
        contents = []
        for content in self.content_api.get(
            "items/content"
        ):  # tqdm(self.content_api.get("items/content"), desc="Downloading content"):
            contents.append(
                {
                    "url_part": content["url_part"],
                    "content": content["content"],
                    "sidebar": content["sidebar"],
                }
            )

        with (self.config.p_data / "content.json").open("w", encoding="utf-8") as file:
            json.dump(contents, file, ensure_ascii=False, indent=4)

    def download_git_content(self):
        repo_path = self.config.p_data / "git_content"
        if not repo_path.exists():
            print("Cloning git repository, this may take a while ...")
            Repo.clone_from(self.config.git_url, repo_path)
            print("... done.")
        else:
            repo = Repo(repo_path)
            origin = repo.remotes.origin
            origin.pull()
            print("Repository updated.")
