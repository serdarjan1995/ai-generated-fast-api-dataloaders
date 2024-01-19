from typing import List, Optional
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyQuery, APIKey
from pydantic import BaseModel

app = FastAPI()

API_KEY = 'YOUR_API_KEY'
API_KEY_NAME = 'access_token'
api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)


class Document(BaseModel):
    text: str


async def get_api_key(api_key_query: str = Depends(api_key_query)):
    if api_key_query == API_KEY:
        return api_key_query
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")


@app.get('/load_data/',
         summary='Load data from Hive',
         description='Read data from the Hive using the provided query.',
         response_model=List[Document])
def load_data_from_hive(
        query: str,
        host: str = None,
        port: int = 10000,  # default port for Hive
        auth: str = 'NONE',  # default auth for Hive
        database: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        key: APIKey = Depends(get_api_key)
):
    try:
        from pyhive import hive
        con = hive.Connection(
            host=host,
            port=port,
            username=username,
            database=database,
            auth=auth,
            password=password,
        )
        cursor = con.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        documents = [Document(text=row) for row in rows]
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
