from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional, Dict
from neo4j import GraphDatabase, basic_auth
import yaml

app = FastAPI()

X_API_KEY = APIKeyHeader(name='X-API-Key')


class Document(BaseModel):
    text: str


@app.on_event('startup')
def create_db_client():
    uri = app.state.config['GRAPH_DB_URI']
    username = app.state.config['GRAPH_DB_USERNAME']
    password = app.state.config['GRAPH_DB_PASSWORD']
    database = app.state.config['GRAPH_DB_NAME']
    app.state.client = GraphDatabase.driver(uri=uri, auth=basic_auth(username, password), encrypted=False)
    app.state.database = database


@app.on_event('shutdown')
def close_db_client():
    app.state.client.close()


@app.post('/load_data/', response_model=List[Document], tags=['GraphDBCypherReader'])
async def load_data(query: str, parameters: Optional[Dict] = None, api_key: APIKey = Depends(validate_api_key)):
    if parameters is None:
        parameters = {}

    records, summary, keys = app.state.client.execute_query(query, parameters, database_=app.state.database)
    documents = [Document(text=yaml.dump(entry.data())) for entry in records]
    return documents


def validate_api_key(api_key: str = Depends(X_API_KEY)):
    if api_key != app.state.config['API_KEY']:
        raise HTTPException(status_code=403, detail='Could not validate credentials')
    return api_key
