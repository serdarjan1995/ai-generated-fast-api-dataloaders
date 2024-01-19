from fastapi import FastAPI, HTTPException, Depends, Security
from typing import Optional
from pydantic import BaseModel, Field
from base import AirbyteStripeReader
from fastapi.security.api_key import APIKeyHeader, APIKey

API_KEY_NAME = 'access_token'
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == 'EXPECTED_API_KEY':
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail='Could not validate credentials')

class ConfigModel(BaseModel):
    client_id: str = Field(..., description='The client ID for Stripe')
    secret_key: str = Field(..., description='The secret key for Stripe')
class AirbyteStripeReaderModel(BaseModel):
    config: ConfigModel

app = FastAPI()

@app.post('/read', response_model=AirbyteStripeReaderModel, summary='Retrieve documents from Stripe',
          description='Endpoint to retrieve documents from Stripe using the AirbyteStripeReader.')
def read_docs(config: ConfigModel, token: APIKey = Depends(get_api_key)):
    stripe_reader = AirbyteStripeReader(config.dict())
    try:
        records = stripe_reader.read_records(stream_slice=None, stream_state=None)
        return {'records': records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
