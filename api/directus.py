import json

import requests


class DirectusAPI:
    def __init__(self, base_url, access_token):
        self.base_url = base_url
        self.access_token = access_token

    def __get_raw(self, endpoint, params = None):
        if params is None:
            params = {}
        for k in params.keys():
            if type(params[k]) is dict:
                params[k] = json.dumps(params[k])
        url = self.base_url + endpoint
        result = requests.get(
          url,
          params = params,
          headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Cache-Control": "no-store"
          }
        )
        return result

    def get(self, endpoint, params = None):
        if params is None:
            params = {}
        result = self.__get_raw(endpoint, params)
        try:
            result_json = result.json()
            if "errors" in result_json.keys():
                print(result_json["errors"])
                raise Exception("Error communicating with API")
            data = result_json["data"]
        except Exception as e:
            print(f"Error: {e}")
            return None
        return data
    
    def get_one(self, endpoint, params = None):
        if params is None:
            params = {}
        results = self.get(endpoint, params)
        if len(results) == 1:
            return results[0]
        elif len(results) == 0:
            return None
        else:
            raise Exception("One result expected, but got more than one result")
            
    def get_file(self, endpoint, params = None):
        if params is None:
            params = {}
        result = self.__get_raw(endpoint, params)
        data = result.content
        if data is None:
            raise Exception("No data from API")
        return data