from fastapi import FastAPI, File, UploadFile, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pathlib import Path
from typing import List
from pdf_nougat_ocr_tool.base import PDFNougatOCR
from pydantic import BaseModel

class Document(BaseModel):
    text: str

app = FastAPI()

API_KEY_NAME = 'access_token'
API_KEY_HEADER = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(API_KEY_HEADER)):
    if api_key_header == "YourActualAPIKey":
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

@app.post("/nougat_ocr/", response_model=List[Document], summary="Perform OCR on a PDF file and return processed text.", description="This endpoint allows you to upload a PDF file and applies nougat OCR to extract text.")
async def nougat_ocr_endpoint(file: UploadFile = File(...), token: str = Security(get_api_key)):
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=415, detail='File must be a PDF.')
    try:
        file_location = f"temp/{file.filename}"
        with open(file_location, 'wb') as f:
            content = await file.read()
            f.write(content)
        pdf_reader = PDFNougatOCR()
        documents = pdf_reader.load_data(Path(file_location))
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to the PDF Nougat OCR tool"}
