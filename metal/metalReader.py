from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel

app = FastAPI()

API_KEY_NAME = 'api_key'
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


class Document(BaseModel):
    text: str


def get_api_key(api_key_header: str = Depends(api_key_header)):
    return api_key_header


@app.post('/load-data', response_model=List[Document])
def load_data(
    api_key: str = Depends(get_api_key),
    client_id: str,
    index_id: str,
    limit: int,
    query_embedding: Optional[List[float]] = None,
    filters: Optional[Dict[str, Dict[str, str]]] = None,
    separate_documents: bool = True
):
    try:
        from metal_sdk.metal import Metal
    except ImportError:
        raise HTTPException(status_code=500, detail="`metal_sdk` package not found, please run `pip install metal_sdk`")

    metal_client = Metal(api_key, client_id, index_id)
    payload = {
        "embedding": query_embedding,
        "filters": filters,
    }
    response = metal_client.search(payload, limit=limit)

    documents = []
    for item in response["data"]:
        text = item["text"] or (item["metadata"] and item["metadata"]["text"])
        documents.append(Document(text=text))

    if not separate_documents:
        text_list = [doc.text for doc in documents]
        text = "\n\n".join(text_list)
        documents = [Document(text=text)]

    return documents
