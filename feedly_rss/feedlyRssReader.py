import json
from typing import List
from fastapi import FastAPI, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

app = FastAPI()
security = HTTPBearer()
class CategoryInput(BaseModel):
    category_name: str
    max_count: int = 100

class EntryOutput(BaseModel):
    title: str
    published: str
    summary: str
    author: str
    content: str
    keywords: List[str]
    commonTopics: List[str]

@app.post('/load_data', response_model=List[EntryOutput])
def load_data(category_input: CategoryInput, credentials: HTTPAuthorizationCredentials = Security(security)):
    from .base import FeedlyRssReader
    token = credentials.credentials
    feedly_reader = FeedlyRssReader(bearer_token=token)
    try:
        documents = feedly_reader.load_data(category_input.category_name, category_input.max_count)
        return [json.loads(doc.text) for doc in documents]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
