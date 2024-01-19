from fastapi import FastAPI, HTTPException, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI()
security = HTTPBasic()

class Document(BaseModel):
    text: str
    embedding: Optional[List[float]] = None

class WeaviateReader:
    def __init__(self, host: str, auth_client_secret: Optional[Any] = None):
        from weaviate import Client
        self.client = Client(host, auth_client_secret=auth_client_secret)

    def load_data(self, class_name: Optional[str], properties: Optional[List[str]], graphql_query: Optional[str], separate_documents: Optional[bool] = True):
        if class_name and properties:
            props_txt = '\n'.join(properties)
            graphql_query = f"""
            {{
                Get {{
                    {class_name} {{
                        {props_txt}
                    }}
                }}
            }}
            """
        elif not graphql_query:
            raise ValueError('Either `class_name` and `properties` must be specified, or `graphql_query` must be specified.')

        response = self.client.query.raw(graphql_query)
        if 'errors' in response:
            raise ValueError(f'Invalid query, got errors: {response['errors']}')

        data_response = response['data']
        if 'Get' not in data_response:
            raise ValueError('Invalid query response, must be a Get query.')

        class_name = class_name or list(data_response['Get'].keys())[0]
        entries = data_response['Get'][class_name]
        documents = [Document(text='\n'.join(f'{k}: {v}' for k, v in entry.items() if k != '_additional'), 
                              embedding=entry.get('_additional', {}).get('vector')) for entry in entries]

        return [Document(text='\n\n'.join(doc.text for doc in documents))] if not separate_documents else documents

@app.post('/load_data', summary='Load data from Weaviate')
def read_data(username: str = Security(security), password: str = Security(security), host: str, class_name: Optional[str] = None, properties: Optional[List[str]] = None, graphql_query: Optional[str] = None, separate_documents: Optional[bool] = True):
    auth_client_secret = weaviate.auth.AuthClientPassword(username=username, password=password)
    reader = WeaviateReader(host=host, auth_client_secret=auth_client_secret)
    try:
        documents = reader.load_data(class_name, properties, graphql_query, separate_documents)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return documents
