import json
import os


class Config:

    def __init__(self):

        self.access_token = None

        if os.path.isfile("config/config.json") :
            with open ("config/config.json") as fh:
                config_doc = json.load(fh)
                self.access_token = config_doc["key"]
        elif 'DIRECTUS_API_KEY' in os.environ.keys():
            self.access_token = os.environ['DIRECTUS_API_KEY']
        else:
            raise Exception("ERROR: Cannot find API key in config or environment!")

        if 'DIRECTUS_BASEURL' in os.environ.keys():
            self.base_url = os.environ['DIRECTUS_BASEURL']
        else:
            self.base_url = "https://fragenkatalog.darc.de/"

        if not self.access_token:
            raise Exception("ERROR: Cannot find API key in config or environment!")
            
  


