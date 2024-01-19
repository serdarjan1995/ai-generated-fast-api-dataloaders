from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI()


class Document(BaseModel):
    text: str
    extra_info: dict


class OpenAlexReader:
    def __init__(self, email: str) -> None:
        self.email = email

    def load_data(self, query: str, full_text: bool = False, fields: Optional[str] = None) -> List[Document]:
        # Implementation of load_data method
        pass


@app.post('/search/',
           summary="Search OpenAlex",
           response_description="List of searched documents",
           response_model=List[Document],
           tags=['Search'])
async def search_openalex(query: str = Query(..., description="Search query", example="biases in large language models"),
                         full_text: bool = Query(False, description="Flag to search in full text"),
                         fields: Optional[str] = Query(None, description="Fields to be returned"),
                         email: str = Query(..., description="Email address for OpenAlex API")):
    openalex_reader = OpenAlexReader(email=email)
    try:
        documents = openalex_reader.load_data(query, full_text, fields)
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

