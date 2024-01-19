from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
from typing import Optional, List
from base import ObsidianReader

app = FastAPI(title='Obsidian Markdown Loader API')


class DocumentModel(BaseModel):
    title: str
    content: str


@app.post('/load', response_model=List[DocumentModel], summary='Load markdown documents',
          description='Load and return documents from the given Obsidian vault path.')
def load_markdown_documents(vault_path: str = Path(..., description='The file system path to the Obsidian vault directory.', example='/path/to/dir')):
    try:
        documents = ObsidianReader(vault_path).load_data()
        return [DocumentModel(title=doc.title, content=doc.body) for doc in documents]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/load/langchain', response_model=List[DocumentModel], summary='Load LangChain formatted documents',
          description='Load and return documents from the given Obsidian vault path in LangChain format.')
def load_langchain_documents(vault_path: str = Path(..., description='The file system path to the Obsidian vault directory.', example='/path/to/dir')):
    try:
        documents = ObsidianReader(vault_path).load_langchain_documents()
        return [DocumentModel(title=doc.title, content=doc.body) for doc in documents]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
