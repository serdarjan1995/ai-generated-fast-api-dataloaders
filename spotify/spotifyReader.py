from typing import List
from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from llama_index.readers.schema.base import Document

app = FastAPI()

API_KEY_NAME = 'access_token'
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


@app.get('/{collection}', response_model=List[Document])
def get_spotify_data(collection: str, api_key: str = Security(api_key_header)):
    from spotify_reader import SpotifyReader
    if api_key is None:
        raise HTTPException(status_code=403, detail='Could not validate credentials')
    try:
        reader = SpotifyReader()
        return reader.load_data(collection=collection)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
