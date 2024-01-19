from fastapi import FastAPI, HTTPException, Query, Depends
from typing import List, Optional, Dict
from pydantic import BaseModel
from fastapi.security.api_key import APIKeyQuery

app = FastAPI()


# Pydantic models for request and response

class DocumentResponse(BaseModel):
    doc_id: str
    text: str
    embedding: List[float]


# Security

def get_api_key(api_key: APIKeyQuery = Depends()):
    if api_key == 'your_api_key':
        return
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")


# Endpoints

@app.post('/load_data/', response_model=List[DocumentResponse])
def load_data(
    query_vector: List[List[float]] = Query(..., description="Query vectors to load data"),
    limit: int = Query(10, description="Number of results to return"),
    where: Optional[Dict] = Query(None, description="Metadata where filter"),
    where_document: Optional[Dict] = Query(None, description="Document where filter"),
    api_key: APIKeyQuery = Depends(get_api_key)
):
    try:
        reader = ChromaReader(collection_name='default_collection', persist_directory='default_directory')
        return reader.load_data(query_vector, limit, where, where_document)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

