from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import uvicorn
from typing import List, Optional
from enum import Enum
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from base import TelegramReader, Document

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

def token_auth(token: str = Depends(oauth2_scheme)):
    if not token or token != 'expected_token':
        raise HTTPException(status_code=401, detail='Invalid or expired token')

@app.post('/token')
def token_login(form_data: OAuth2PasswordRequestForm = Depends()):
    return {'access_token': 'test_token', 'token_type': 'bearer'}

@app.get('/load_data', response_model=List[Document])
def load_data(
    entity_name: str,
    post_id: Optional[int] = None,
    limit: Optional[int] = None,
    token: str = Depends(token_auth)
):
    loader = TelegramReader(session_name='session_name_placeholder', api_id=123456, api_hash='api_hash_placeholder', phone_number='+123456789')
    return loader.load_data(entity_name=entity_name, post_id=post_id, limit=limit)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)