from typing import List
from fastapi import FastAPI, HTTPException, Body, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
import requests

app = FastAPI()

API_KEY_NAME = 'access_token'
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

BASE_URL = "https://api.patentsview.org/patents/query"

class Document(BaseModel):
    text: str

class PatentQuery(BaseModel):
    patent_number: List[str]

async def get_api_key(api_key_header: str = Depends(api_key_header)):
    if api_key_header != "expected_api_key":
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key_header

@app.post('/load_data', response_model=List[Document], summary='Fetch patent abstracts')
async def load_data(query: PatentQuery = Body(..., embed=True),
                   api_key: str = Depends(get_api_key)):
    if not query.patent_number:
        raise HTTPException(status_code=400, detail='Please input patent numbers')

    json_payload = {"q": {"patent_id": query.patent_number}, "f": ["patent_abstract"]}
    response = requests.post(BASE_URL, json=json_payload)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail='Request failed')

    data = response.json().get('patents', [])
    return [Document(text=patent['patent_abstract']) for patent in data]
