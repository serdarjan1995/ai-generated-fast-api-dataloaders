from typing import List, Optional
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from base import ChatGPTRetrievalPluginReader, Document

app = FastAPI()

security = HTTPBearer()

def get_current_bearer_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials:
        return credentials.credentials
    else:
        raise HTTPException(status_code=403, detail='Not authenticated')


@app.post('/query', response_model=List[Document])
async def read_query(
    query: str,
    top_k: Optional[int] = 10,
    separate_documents: Optional[bool] = True,
    bearer_token: str = Depends(get_current_bearer_token)
):
    """Search for documents.

    Args:
        query: The text query to retrieve documents for.
        top_k: Number of top documents to retrieve.
        separate_documents: Whether to return documents separately or as a single concatenated text.
        bearer_token: Authentication token required to access the endpoint.
    """
    reader = ChatGPTRetrievalPluginReader(
        endpoint_url='http://localhost:8000',
        bearer_token=bearer_token
    )
    try:
        return reader.load_data(query, top_k, separate_documents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
