from tavily import AsyncTavilyClient
from utils.getAPI import getApiKey
import json

class WebSearchTool():
    def __init__(self):
        self.tavily_client = AsyncTavilyClient(api_key=getApiKey("TAVILY_API_KEY")) 

        with open(getApiKey("PLACE_JSON_PATH"), "r", encoding="utf-8") as file:
            self.place_json = json.load(file)

    def check_place(self, place: str):
        if place in self.place_json:
            return True 
        else:
            return False 


    async def search_query(self, place):
        response = await self.tavily_client.search(f"{place}는 어떤 곳인가요?") 
        return response

