from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from typing import List
import requests
from pydantic import BaseModel

app = FastAPI()

API_KEY_NAME = 'Authorization'
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


# Pydantic models

class Document(BaseModel):
    text: str
    extra_info: dict

class LinearReader:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def load_data(self, query: str) -> List[Document]:
        graphql_endpoint = "https://api.linear.app/graphql"
        headers = {'Authorization': self.api_key, 'Content-Type': 'application/json'}
        payload = {'query': query}
        response = requests.post(graphql_endpoint, json=payload, headers=headers)
        data = response.json()

        issues = []
        team_data = data.get('data', {}).get('team', {})
        for issue in team_data.get('issues', {}).get('nodes', []):
            document = Document(
                text=f"{issue['title']} \n {issue['description']}",
                extra_info=issue
            )
            issues.append(document)
        return issues

@app.post('/load_data/', response_model=List[Document])
async def load_data(query: str, api_key: APIKeyHeader = Security(api_key_header)):
    linear_reader = LinearReader(api_key=api_key)
    return linear_reader.load_data(query=query)
