from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import shutil
from base import HWPReader

app = FastAPI()


class Document(BaseModel):
    text: str
    extra_info: Optional[dict] = None


@app.post('/load_data/', response_model=Document, summary='Load and process an HWP file',
           description='Accepts an HWP file and returns the extracted text as a Document object.')
async def load_data(file: UploadFile = File(..., description='The HWP file to be processed.')):
    with open(file.filename, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
    hwp_path = Path(file.filename)
    reader = HWPReader()
    documents = reader.load_data(file=hwp_path)
    return documents[0]
