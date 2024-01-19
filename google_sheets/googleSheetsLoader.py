from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from typing import List
from pydantic import BaseModel

app = FastAPI(title='Google Sheets Loader')

API_KEY = 'your-api-key-here'
API_KEY_NAME = 'access_token'
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(status_code=403, detail='Could not validate credentials')


class Document(BaseModel):
    text: str
    extra_info: dict = None
    meta: dict = None

class SpreadsheetLoad(BaseModel):
    spreadsheet_id: str

class SpreadsheetLoadAsDocs(BaseModel):
    spreadsheet_id: str
    sheet_name: str
    text_column_name: str = 'text'


@app.post('/load_data/', response_model=List[Document])
def load_data(spreadsheet_ids: List[str], api_key: APIKeyHeader = Depends(get_api_key)):
    # Implementation of load_data from the GoogleSheetsReader class
    pass

@app.post('/load_sheet_as_documents/', response_model=List[Document])
def load_sheet_as_documents(spreadsheets: SpreadsheetLoadAsDocs, api_key: APIKeyHeader = Depends(get_api_key)):
    # Implementation of load_sheet_as_documents from the GoogleSheetsReader class
    pass
