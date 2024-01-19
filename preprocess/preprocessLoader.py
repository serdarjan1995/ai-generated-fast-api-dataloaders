from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyQuery, APIKey
from typing import Optional, List
from pydantic import BaseModel

app = FastAPI(title='Preprocess Loader')

API_KEY = 'test'  # Placeholder for the actual API key mechanism
API_KEY_NAME = 'access_token'
api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)


def get_api_key(api_key_query: str = Security(api_key_query)):
    if api_key_query == API_KEY:
        return api_key_query
    else:
        raise HTTPException(status_code=403, detail='Could not validate credentials')

class DocumentInput(BaseModel):
    filepath: Optional[str]
    process_id: Optional[str]
    return_whole_document: Optional[bool] = False

class DocumentOutput(BaseModel):
    text: str
    filename: str

@app.post('/load_data', response_model=List[DocumentOutput])
def load_data(document_input: DocumentInput, api_key: APIKey = Security(get_api_key)):
    preprocess_reader = PreprocessReader(api_key=api_key, **document_input.dict(exclude_unset=True))
    documents = preprocess_reader.load_data(document_input.return_whole_document)
    return [{'text': doc.text, 'filename': doc.metadata.get('filename')} for doc in documents]

@app.get('/get_nodes')
def get_nodes(filepath: str, api_key: APIKey = Security(get_api_key)):
    preprocess_reader = PreprocessReader(api_key=api_key, filepath=filepath)
    nodes = preprocess_reader.get_nodes()
    return nodes

@app.get('/get_process_id')
def get_process_id(filepath: str, api_key: APIKey = Security(get_api_key)):
    preprocess_reader = PreprocessReader(api_key=api_key, filepath=filepath)
    process_id = preprocess_reader.get_process_id()
    return {'process_id': process_id}
