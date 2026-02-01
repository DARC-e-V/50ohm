from git import Repo

from api.directus import DirectusAPI

from .config import Config


class Download:
    def __init__(self, content_api: DirectusAPI, config: Config):
        self.config = config
        self.content_api = content_api

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
