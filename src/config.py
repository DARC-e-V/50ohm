import json
import os
from pathlib import Path


class Config:
    __env_prefix = "OHM"

    def __init__(self):
        if os.path.isfile("config/config.json"):
            with open("config/config.json") as file:
                self.config = json.load(file)
        else:
            self.config = {}

        self.content_access_token = self.get_config_value("directus_content_api_key")
        self.content_base_url = self.get_config_value("directus_content_base_url", "https://redaktion.50ohm.de/")
        self.git_url = self.get_config_value("git_url", "git@github.com:DARC-e-V/50ohm-contents-dl.git")

        self.p_fragenkatalog = Path(
            self.get_config_value("path_fragenkatalog", "./data/git_content/contents/questions/fragenkatalog3b.json")
        )

        self.p_data = Path("./data")
        self.p_data_photos = self.p_data / "git_content" / "photos"
        self.p_data_pictures = self.p_data / "git_content" / "pictures"

        self.p_build = Path("./build")
        self.p_build_photos = self.p_build / "photos"
        self.p_build_pictures = self.p_build / "pictures"
        self.p_build_assets = self.p_build / "assets"

        self.p_assets = Path("./assets")

    def get_config_value(self, key: str, default=None):
        if key in self.config:
            return self.config[key]
        elif f"{self.__env_prefix}_{key.upper()}" in os.environ.keys():
            return os.environ[f"{self.__env_prefix}_{key.upper()}"]
        elif default is not None:
            return default
        else:
            raise Exception(
                f"ERROR: Required value for '{key}' not found."
                f"Add to config.json or env as '${self.__env_prefix}_{key.upper()}'"
            )
