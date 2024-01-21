from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional
from enum import Enum
import uvicorn
from pydantic import BaseModel

app = FastAPI()

class Document(BaseModel):
    text: str
    extra_info: dict

@app.get('/load_data_bioc/', summary='Load data from Pubmed using Bioc API', response_model=List[Document])
async def load_data_bioc(
    search_query: str = Query(..., description='A topic to search for (e.g. "Alzheimers").', example='Alzheimers'),
    max_results: Optional[int] = Query(10, description='Maximum number of papers to fetch.', example=10)
) -> List[Document]:
    from base import PubmedReader
    pubmed_reader = PubmedReader()
    try:
        return pubmed_reader.load_data_bioc(search_query, max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/load_data/', summary='Load data from Pubmed', response_model=List[Document])
async def load_data(
    search_query: str = Query(..., description='A topic to search for (e.g. "Alzheimers").', example='Alzheimers'),
    max_results: Optional[int] = Query(10, description='Maximum number of papers to fetch.', example=10)
) -> List[Document]:
    from base import PubmedReader
    pubmed_reader = PubmedReader()
    try:
        return pubmed_reader.load_data(search_query, max_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)