from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from fastapi.security.api_key import APIKeyHeader
import llama_hub.milvus as MilvusReader

api_key_header_auth = APIKeyHeader(name="X-API-KEY", auto_error=False)

app = FastAPI(title="Milvus Loader", openapi_url="/api/v1/openapi.json")


async def get_api_key(api_key_header: str = Depends(api_key_header_auth)):
    if api_key_header != "YourSecretAPIKey":
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key_header


class QueryModel(BaseModel):
    query_vector: List[float]
    collection_name: str
    limit: int = 10


@app.post("/load_data/", tags=["Milvus Loader"])
def load_data_endpoint(query: QueryModel, token: str = Depends(get_api_key)):
    reader = MilvusReader(
        host="localhost",
        port=19530,
        user="<user>",
        password="<password>",
        use_secure=False,
    )
    documents = reader.load_data(
        query_vector=query.query_vector,
        collection_name=query.collection_name,
        limit=query.limit,
    )
    return documents


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
