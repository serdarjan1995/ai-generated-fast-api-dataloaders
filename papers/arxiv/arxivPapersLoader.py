from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from base import ArxivReader, Document

app = FastAPI(title='Arxiv Papers Loader')

@app.post('/load_data/', response_model=List[Document], summary='Load papers and abstracts')
def load_data(search_query: str, papers_dir: Optional[str] = '.papers', max_results: Optional[int] = 10):
    try:
        loader = ArxivReader()
        documents = loader.load_data(search_query, papers_dir, max_results)
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/load_papers_and_abstracts/', response_model=List[Document], summary='Load papers and abstracts separately')
def load_papers_and_abstracts(search_query: str, papers_dir: Optional[str] = '.papers', max_results: Optional[int] = 10):
    try:
        loader = ArxivReader()
        papers, abstracts = loader.load_papers_and_abstracts(search_query, papers_dir, max_results)
        return {'papers': papers, 'abstracts': abstracts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))