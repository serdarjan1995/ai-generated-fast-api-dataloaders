
from fastapi import FastAPI, Query, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyQuery, APIKey
from typing import List
import numpy as np
from pydantic import BaseModel
import deeplake

app = FastAPI()

API_KEY = 'your-api-key-here'
API_KEY_NAME = 'access_token'
api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)

class Document(BaseModel):
    doc_id: str
    text: str

def get_api_key(
    api_key_query: str = Security(api_key_query),
):
    if api_key_query == API_KEY:
        return api_key_query
    else:
        raise HTTPException(status_code=403, detail='Could not validate credentials')

@app.post('/vector_search', 
          summary='Search for nearest neighbors of a query vector.',
          response_model=List[int])
def vector_search(
    query_vector: List[float] = Query(..., description='Query vector for search.'),
    data_vectors: List[List[float]] = Query(..., description='Data vectors for search.'),
    distance_metric: str = Query('l2', description='Distance metric used for finding nearest neighbors.', enum=['l2', 'l1', 'max', 'cos', 'dot']),
    limit: int = Query(4, description='Number of nearest neighbors to find.')
):
    data_vectors_np = np.array(data_vectors)
    query_vector_np = np.array(query_vector).reshape(1, -1)
    distances = distance_metric_map[distance_metric](query_vector_np, data_vectors_np)
    nearest_indices = np.argsort(distances)
    nearest_indices = nearest_indices[::-1][:limit] if distance_metric == 'cos' else nearest_indices[:limit]
    return nearest_indices.tolist()

@app.post('/load_data', 
          summary='Load and return documents from a DeepLake dataset.',
          response_model=List[Document])
def load_data(
    token: str = Depends(get_api_key),
    query_vector: List[float] = Query(..., description='Query vector for retrieving documents.'),
    dataset_path: str = Query(..., description='Path to the DeepLake dataset.'),
    limit: int = Query(4, description='Maximum number of documents to return.'),
    distance_metric: str = Query('l2', description='Distance metric used for retrieving nearest neighbors.', enum=['l2', 'l1', 'max', 'cos', 'dot'])
):
    dataset = deeplake.load(dataset_path, token=token)
    try:
        embeddings = dataset.embedding.numpy(fetch_chunks=True)
    except Exception:
        raise HTTPException(status_code=404, detail='Embedding not found')

    indices = vector_search(query_vector, embeddings, distance_metric=distance_metric, limit=limit)
    
    documents = []
    for idx in indices:
        document = Document(
            doc_id=dataset[idx].ids.numpy().tolist()[0],
            text=str(dataset[idx].text.numpy().tolist()[0]),
        )
        documents.append(document)

    return documents
  