
from fastapi import FastAPI, HTTPException, Request, Depends, Body, APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()
security = HTTPBasic()

class Document(BaseModel):
    text: str
    extra_info: dict

class GuruReader:
    def __init__(self, guru_username: str, api_token: str):
        self.guru_username = guru_username
        self.api_token = api_token
        self.guru_auth = HTTPBasicAuth(guru_username, api_token)

    def load_data(self, collection_ids: Optional[List[str]] = None, card_ids: Optional[List[str]] = None) -> List[Document]:
        if collection_ids is not None:
            card_ids = self._get_card_ids_from_collection_ids(collection_ids)

        return [self._get_card_info(card_id) for card_id in card_ids]

    def _get_card_ids_from_collection_ids(self, collection_ids: List[str]) -> List[str]:
        all_ids = []
        for collection_id in collection_ids:
            card_ids = self._get_card_ids_from_collection_id(collection_id)
            all_ids.extend(card_ids)
        return all_ids

    # The rest of the methods are defined here (skipping for brevity)

router = APIRouter()

@router.get( '/load-data', summary='Load data from Guru', response_model=List[Document])
async def read_collection_cards(credentials: HTTPBasicCredentials = Depends(security), collection_ids: Optional[List[str]] = Body(None, description='List of collection IDs to load from'), card_ids: Optional[List[str]] = Body(None, description='List of card IDs to load from')):
    guru_reader = GuruReader(credentials.username, credentials.password)
    try:
        return guru_reader.load_data(collection_ids, card_ids)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))

app.include_router(router, prefix='/guru', tags=['Guru Reader'])

def get_application():
  return app
