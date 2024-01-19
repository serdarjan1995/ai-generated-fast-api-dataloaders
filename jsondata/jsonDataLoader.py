from fastapi import FastAPI, HTTPException, Query, Security
from fastapi.security.api_key import APIKeyQuery
from typing import Union
from pydantic import BaseModel
from base import JsonDataReader

app = FastAPI()


@app.post('/load_json/', summary='Load JSON data', response_model=List[str])
def load_json(data: Union[str, dict], api_key: APIKeyQuery = Security(APIKeyQuery(name='api_key', auto_error=True))):
    """Load JSON data from a JSON string or a dictionary.
 
    - **data**: JSON string or dict to be processed.
    - **api_key**: API key for secure access.
    """
    try:
        reader = JsonDataReader()
        documents = reader.load_data(data)
        return [doc.text for doc in documents]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
