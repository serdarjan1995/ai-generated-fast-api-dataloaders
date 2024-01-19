from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from typing import List
from pydantic import BaseModel

app = FastAPI()


X_API_KEY = 'your_api_key_here'  # Predefined API Key, should be generated and kept secret
api_key_header = APIKeyHeader(name='X-API-Key', auto_error=False)


def get_api_key(
    api_key: str = Depends(api_key_header),
):
    if api_key != X_API_KEY:
        raise HTTPException(status_code=403, detail='Could not validate credentials')
    return api_key


class Document(BaseModel):
    text: str
    extra_info: dict = None


class SmartPDFLoader(BaseModel):
    llmsherpa_api_url: str = None

    def load_data(self, pdf_path_or_url: str) -> List[Document]:
        # Logic to load data from a PDF and return as list of `Document`
        pass  # Should implement the actual processing logic here


@app.post('/load_data/', response_model=List[Document], summary='Load and parse PDF document', description='Load data and extract table from PDF')
async def load_data_endpoint(pdf_path_or_url: str, api_loader: SmartPDFLoader = Depends(), api_key: str = Depends(get_api_key)):
    try:
        results = api_loader.load_data(pdf_path_or_url)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
