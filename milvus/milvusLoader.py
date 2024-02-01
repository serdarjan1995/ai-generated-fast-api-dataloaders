from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import List
from fastapi.security.api_key import APIKeyHeader
import llama_hub.milvus as MilvusReader

api_key_header_auth = APIKeyHeader(name="X-API-KEY", auto_error=False)

app = FastAPI(title="Milvus Loader", openapi_url="/api/v1/openapi.json")


class QueryModel(BaseModel):
    query_vector: List[float]
    collection_name: str
    limit: int = 10


class RequestModel(BaseModel):
    host: str
    port: int = 19530
    user: str
    password: str
    use_secure: bool = False
    query: QueryModel


@app.post("/load_data/", tags=["Milvus Loader"])
def load_data_endpoint(request: RequestModel = Body(...)):
    print(request)
    reader = MilvusReader(
        host=request.host,
        port=request.port,
        user=request.user,
        password=request.password,
        use_secure=request.use_secure,
    )
    documents = reader.load_data(
        query_vector=request.query.query_vector,
        collection_name=request.query.collection_name,
        limit=request.query.limit,
    )
    return documents
