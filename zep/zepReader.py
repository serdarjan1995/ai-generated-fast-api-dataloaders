from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional, Dict, Any
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel

app = FastAPI()

api_key_header = APIKeyHeader(name='Authorization', auto_error=False)


class Document(BaseModel):
    text: str
    embedding: Optional[List[float]] = None


def get_api_key(api_key_header: str = Depends(api_key_header)):
    if api_key_header == 'optional_api_key':
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail='Could not validate credentials')


@app.post('/load_data/', response_model=List[Document])
def load_data(
    collection_name: str,
    query: Optional[str] = None,
    vector: Optional[List[float]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    top_k: Optional[int] = 5,
    separate_documents: Optional[bool] = True,
    include_values: Optional[bool] = True,
    api_key: str = Depends(get_api_key)
):
    """
    Load data from a Zep collection.

    - **collection_name**: Name of the Zep collection.
    - **query**: Query string.
    - **vector**: Query vector.
    - **metadata**: Metadata to filter on.
    - **top_k**: Number of results to return.
    - **separate_documents**: Whether to return separate documents per retrieved entry.
    - **include_values**: Whether to include the embedding in the response.
    - **api_key**: API key for accessing Zep API.
    """
    reader = ZepReader(api_url=api_key, api_key=api_key)
    try:
        results = reader.load_data(
            collection_name=collection_name,
            query=query,
            vector=vector,
            metadata=metadata,
            top_k=top_k,
            separate_documents=separate_documents,
            include_values=include_values
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return results
