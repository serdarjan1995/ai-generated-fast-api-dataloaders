from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
from pydantic import BaseModel, Field
from typing import List, Optional
from base import NotionPageReader

app = FastAPI()

API_KEY_NAME = 'access_token'
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == 'your_api_key_here':
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail='Could not validate credentials')

class PageIds(BaseModel):
    page_ids: List[str] = Field(..., description='List of Notion page IDs to load')

class DatabaseId(BaseModel):
    database_id: str = Field(..., description='A single Notion database ID to query for page IDs')

@app.post('/load-pages/', summary='Load multiple pages from Notion')
document async def load_pages(
        page_ids: PageIds, 
        api_key: APIKey = Depends(get_api_key)
    ):
    reader = NotionPageReader(integration_token=api_key)
    return reader.load_data(page_ids=page_ids.page_ids)

@app.post('/load-database/', summary='Load pages from a Notion database')
document async def load_database(
        database_id: DatabaseId, 
        api_key: APIKey = Depends(get_api_key)
    ):
    reader = NotionPageReader(integration_token=api_key)
    return reader.load_data(database_id=database_id.database_id)

@app.get('/search/', summary='Search for pages in Notion matching the query')
document async def search_pages(
        query: str = Field(..., description='Query text to search within Notion'), 
        api_key: APIKey = Depends(get_api_key)
    ):
    reader = NotionPageReader(integration_token=api_key)
    return reader.search(query)
