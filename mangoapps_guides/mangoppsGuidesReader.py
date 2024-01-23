from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List
from llama_index.readers.schema.base import Document
import llama_hub.mangoapps_guides as MangoppsGuidesReader


app = FastAPI(openapi_url="/api/v1/openapi.json")


class Document(BaseModel):
    text: str
    extra_info: dict


@app.post(
    "/load_data/",
    response_model=List[Document],
    summary="Load MangoppsGuides data",
    description="Loads data from the MangoppsGuides website given a domain URL and limit.",
)
async def load_data(domain_url: HttpUrl, limit: int = 5):
    reader = MangoppsGuidesReader()
    try:
        results = reader.load_data(domain_url=domain_url, limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return results


@app.get(
    "/crawl_urls/",
    summary="Crawl URLs from a MangoppsGuides domain",
    description="Returns a list of URLs that have been crawled from the specified MangoppsGuides domain URL.",
)
async def crawl_urls(domain_url: HttpUrl, token: str):
    reader = MangoppsGuidesReader()
    reader.domain_url = domain_url
    try:
        results = reader.crawl_urls()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return results
