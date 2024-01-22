from typing import List
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
from pydantic import BaseModel
import requests
import json

app = FastAPI(openapi_url="/api/v1/openapi.json")

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=True)


async def get_api_key(api_key_header: str = Depends(API_KEY_HEADER)):
    return api_key_header


class Document(BaseModel):
    text: str
    extra_info: dict


class MacrometaGDNReader:
    def __init__(self, url: str, apikey: str):
        self.url = url
        self.apikey = apikey

    def load_data(self, collection_list: List[str]) -> List[Document]:
        if not collection_list:
            raise ValueError("Must specify collection name(s)")
        results = []
        for collection_name in collection_list:
            documents = json.loads(self._load_collection(collection_name))
            for doc in documents:
                results.append(
                    Document(text=doc, extra_info={"collection_name": collection_name})
                )
        return results

    def _load_collection(self, collection_name: str) -> str:
        url = f"{self.url}/_fabric/_system/_api/cursor"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"apikey {self.apikey}",
        }
        data = {
            "batchSize": 1000,
            "ttl": 60,
            "query": f"FOR doc IN {collection_name} RETURN doc",
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_json = response.json()
        if response.status_code == 201:
            all_documents = response_json.get("result", [])
        else:
            raise HTTPException(
                status_code=response.status_code, detail="Failed to load documents"
            )
        return str(all_documents)


@app.post("/load_data/", response_model=List[Document])
async def load_data_endpoint(
    collection_names: List[str], api_key: APIKey = Depends(get_api_key)
):
    reader = MacrometaGDNReader("https://api-macrometa.io", apikey=api_key)
    try:
        return reader.load_data(collection_list=collection_names)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
