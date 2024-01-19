from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel

app = FastAPI()

API_KEY_NAME = 'X-API-KEY'
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


class GraphQLQuery(BaseModel):
    query: str
    variables: Optional[Dict] = None


class Document(BaseModel):
    text: str


@app.post('/graphql', response_model=List[Document], summary='Perform GraphQL query', description='This endpoint allows you to perform a GraphQL query on a given endpoint with optional variables.', tags=['GraphQL Loader'])
async def execute_graphql_query(query: GraphQLQuery, api_key: str = Security(api_key_header)):
    if api_key != 'your_api_key':
        raise HTTPException(status_code=403, detail='Could not validate credentials')

    try:
        from gql import gql, Client
        from gql.transport.requests import RequestsHTTPTransport
    except ImportError:
        raise ImportError('The gql package is required to perform GraphQL queries')

    headers = {}
    transport = RequestsHTTPTransport(url='https://your.graphql.api/endpoint', headers=headers)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    documents = []
    result = client.execute(gql(query.query), variable_values=query.variables)

    for key in result:
        entry = result[key]
        if isinstance(entry, list):
            documents.extend([Document(text=str(v)) for v in entry])
        else:
            documents.append(Document(text=str(entry)))

    return documents
