from typing import List, Optional
from fastapi import FastAPI, HTTPException, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from sqlalchemy.engine import Engine
from base import SnowflakeReader

class Query(BaseModel):
    query: str

app = FastAPI()
security = HTTPBasic()

@app.post('/load_data', summary='Load data from Snowflake')
def load_data_from_snowflake(
    query: Query,
    credentials: HTTPBasicCredentials = Security(security),
    account: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    database: Optional[str] = None,
    schema: Optional[str] = None,
    warehouse: Optional[str] = None,
    role: Optional[str] = None,
    proxy: Optional[str] = None,
    engine: Optional[Engine] = None
) -> List:
    if not credentials.username or not credentials.password:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    reader = SnowflakeReader(account, user, credentials.password, database, schema, warehouse, role, proxy, engine)
    try:
        documents = reader.load_data(query=query.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return documents

