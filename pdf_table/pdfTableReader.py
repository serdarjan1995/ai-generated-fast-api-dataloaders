from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import shutil
import uuid

app = FastAPI()

X_API_KEY = 'your-api-key'
api_key_header = APIKeyHeader(name='X-API-Key', auto_error=False)


class Document(BaseModel):
    text: str
    extra_info: Optional[dict] = {}


@app.post('/load_data/',
          summary='Extract tables from a PDF file',
          response_model=List[Document])
async def load_data(
        file: UploadFile = File(..., description='PDF file to extract tables from.'),
        pages: str = Form('1', description='Pages to read tables from.'),
        extra_info: Optional[dict] = Form(None, description='Extra information.'),
        token: Optional[str] = api_key_header
    ):

    if token != X_API_KEY:
        raise HTTPException(status_code=403, detail='Invalid API Key')

    file_path = Path('/tmp') / f'{uuid.uuid4()}.pdf'
    with file_path.open('wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    document = PDFTableReader().load_data(file=file_path, pages=pages, extra_info=extra_info)
    return document


@app.on_event('startup')
async def startup_event():
    print('Starting PDF Table Reader service...')


@app.on_event('shutdown')
async def shutdown_event():
    print('Shutting down PDF Table Reader service...')
