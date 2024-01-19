from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

API_KEY = 'your-api-key'
API_KEY_NAME = 'access_token'
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

class Document(BaseModel):
    text: str
    extra_info: dict

class JoplinReader:
    # ... (place your modified JoplinReader class here, without docstrings and with adjustments if needed)

@app.post('/load_data/', summary='Load documents', description='Load documents from Joplin with the provided API key.')
def load_documents(api_key: str = Security(get_api_key)):
    reader = JoplinReader(access_token=api_key)
    documents = reader.load_data()
    return documents
