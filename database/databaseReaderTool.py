from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from base import DatabaseReader

app = FastAPI()

class Document(BaseModel):
    text: str

class DatabaseConfig(BaseModel):
    scheme: str
    host: str
    port: str
    user: str
    password: str
    dbname: str

@app.post('/load_data/', response_model=List[Document])
def load_data(
        query: str = Query(..., description='Query parameter to filter tables and rows'),
        database_config: Optional[DatabaseConfig] = None,
        uri: Optional[str] = Query(None, description='URI of the database connection'),
        token: Optional[str] = Query(None, description='Access token for authorization, if required')
    ):
    try:
        if database_config:
            reader = DatabaseReader(scheme=database_config.scheme, host=database_config.host, port=database_config.port, user=database_config.user, password=database_config.password, dbname=database_config.dbname)
        elif uri:
            reader = DatabaseReader(uri=uri)
        else:
            raise HTTPException(status_code=400, detail='Insufficient database connection parameters')
        documents = reader.load_data(query)
        return documents
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))