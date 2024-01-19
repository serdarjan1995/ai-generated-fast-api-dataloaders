from typing import List
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from base import MondayReader

app = FastAPI()

API_KEY_NAME = 'X-API-Key'
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


class DocumentModel(BaseModel):
    text: str
    extra_info: dict


def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == "expected_api_key_value":
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

@app.get("/", summary="Health Check", description="Checks if the service is running")
def health_check():
    return {"status": "Service is up and running"}

@app.post("/load_data", response_model=List[DocumentModel], summary="Load data from monday.com", description="Loads a board's data from monday.com using the provided board id", dependencies=[Depends(get_api_key)])
def load_data(board_id: int, api_key: str = Depends(get_api_key)):
    reader = MondayReader(api_key)
    try:
        return reader.load_data(board_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
