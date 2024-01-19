from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from wikipedia import page, set_lang
from wikipedia.exceptions import DisambiguationError, PageError

app = FastAPI()


class Document(BaseModel):
    text: str


class LoadDataRequest(BaseModel):
    pages: List[str] = Field(..., title='Page Titles', description='List of Wikipedia page titles to fetch.')
    lang: str = Field('en', title='Language Code', description='The language of the Wikipedia to query.')


class LoadDataResponse(BaseModel):
    documents: List[Document]


@app.post('/load_data', response_model=LoadDataResponse, summary='Load Data from Wikipedia', description='Fetches text from an array of Wikipedia page titles.')
async def load_data(request: LoadDataRequest):
    set_lang(request.lang)
    results = []
    for page_title in request.pages:
        try:
            page_content = page(page_title).content
            results.append(Document(text=page_content))
        except DisambiguationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except PageError:
            raise HTTPException(status_code=404, detail=f'Page {page_title} does not exist.')
    return LoadDataResponse(documents=results)
