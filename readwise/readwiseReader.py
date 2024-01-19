from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
import uvicorn

app = FastAPI(title='Readwise Reader')

API_KEY_NAME = 'access_token'
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


class Document(BaseModel):
    text: str


def get_readwise_data(api_key: str, updated_after: Optional[datetime] = None):
    import requests
    result = []
    next_page = None
    params = {'pageCursor': next_page, 'updatedAfter': updated_after.isoformat() if updated_after else None}
    while True:
        response = requests.get(url='https://readwise.io/api/v2/export/', params=params, headers={'Authorization': f'Token {api_key}'}),
        response.raise_for_status()
        data = response.json()
        result.extend(data['results'])
        next_page = data.get('nextPageCursor')
        if not next_page:
            break
    return result


def get_documents(readwise_data: List):
    return [Document(text=json.dumps(d)) for d in readwise_data]


@app.get('/load_data', summary='Load Readwise highlights', description='Load highlights from Readwise and return as documents', response_model=List[Document])
async def load_data(api_key: str = Security(api_key_header), updated_after: Optional[datetime] = None):
    try:
        readwise_data = get_readwise_data(api_key=api_key, updated_after=updated_after)
        documents = get_documents(readwise_data)
        return documents
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
