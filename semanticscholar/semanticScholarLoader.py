from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from typing import List, Optional
from pydantic import BaseModel
from base import SemanticScholarReader, Document

app = FastAPI()

X_API_KEY = APIKeyHeader(name='X-API-Key', auto_error=False)


class DocumentResponse(BaseModel):
    text: Optional[str]
    extra_info: dict


@app.get('/load_data',
          response_model=List[DocumentResponse],
          summary='Load data from Semantic Scholar',
          description='Loads scholarly articles and publications based on the query provided')
def load_data(query: str,
              limit: int = 10,
              full_text: bool = False,
              returned_fields: List[str] = ['title', 'abstract', 'venue', 'year', 'paperId', 'citationCount', 'openAccessPdf', 'authors'],
              key: Optional[str] = Security(X_API_KEY)):
    if not key:
        raise HTTPException(status_code=403, detail='API key required')
    try:
        s2reader = SemanticScholarReader(api_key=key)
        documents = s2reader.load_data(query, limit, full_text, returned_fields)
        return [{'text': doc.text, 'extra_info': doc.extra_info} for doc in documents]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
