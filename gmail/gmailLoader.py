from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from typing import List
from pydantic import BaseModel
from llama_hub.gmail import GmailReader


app = FastAPI()

API_KEY_NAME = 'access_token'
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class Document(BaseModel):
    text: str
    extra_info: dict


class QueryModel(BaseModel):
    query: str = 'from: me label:inbox'
    max_results: int = 10
    results_per_page: int = 10
    use_iterative_parser: bool = False


@app.post('/read_gmail', response_model=List[Document])
async def read_gmail(
        query: QueryModel,
        #token: str = Depends(api_key_header)
):
    gmail_reader = GmailReader(
        query=query.query,
        max_results=query.max_results,
        results_per_page=query.results_per_page,
        use_iterative_parser=query.use_iterative_parser
    )
    return gmail_reader.load_data()
