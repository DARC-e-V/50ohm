import json
import os


class Config:
    env_prefix = "OHM"
    access_token: str
    base_url: str
    no_latex: bool

    def __init__(self):
        if os.path.isfile("config/config.json"):
            with open("config/config.json") as file:
                self.config = json.load(file)

        self.access_token = self.get_config_value("directus_api_key")
        self.base_url = self.get_config_value("directus_api_url", "https://fragenkatalog.darc.de/")
        self.no_latex = self.get_config_value("no_latex", False)

    def get_config_value(self, key: str, default=None):
        if key in self.config:
            return self.config[key]
        elif f"{self.env_prefix}_{key.upper()}" in os.environ.keys():
            return os.environ[f"{self.env_prefix}_{key.upper()}"]
        elif default is not None:
            return default
        else:
            raise Exception(
                f"ERROR: Required value for '{key}' not found. Add to config.json or env as '${self.env_prefix}_{key.upper()}'"
            )
