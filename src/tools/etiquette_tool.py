import json
if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.getAPI import getApiKey


class Etiquette_Tool():
    def __init__(self):
        with open(getApiKey("ETIQUETTE_JSON_PATH"), "r", encoding="utf-8") as file:
            self.etiquette_json = json.load(file) 


    def get_etiquette(self, category):
        if category in self.etiquette_json:
            return self.etiquette_json[category]
        else:
            return None 



if __name__ == "__main__":
    test = Etiquette_Tool()
     