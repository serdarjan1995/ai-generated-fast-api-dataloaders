from typing import List
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from enum import Enum

app = FastAPI()

class Document(BaseModel):
    text: str

class StringIterableReader:
    @classmethod
    def load_data(cls, texts: List[str]) -> List[Document]:
        return [Document(text=text) for text in texts]

@app.post('/load', summary='Load string iterable as documents', response_model=List[Document])
async def load_data(texts: List[str] = Query(..., description='A list of texts to be loaded')):
    if not texts:
        raise HTTPException(status_code=400, detail='Texts list cannot be empty.')
    return StringIterableReader.load_data(texts=texts)
