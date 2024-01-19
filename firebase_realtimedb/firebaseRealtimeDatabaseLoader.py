from typing import List
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel

app = FastAPI()

API_KEY_NAME = 'access_token'
API_KEY = 'your_api_key_here'

api_key_header_auth = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Depends(api_key_header_auth)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail='Could not validate credentials')

class Document(BaseModel):
    text: str
    extra_info: dict

def initialize_firebase(database_url: str, service_account_key_path: str = None):
    import firebase_admin
    from firebase_admin import credentials
    if not firebase_admin._apps:
        if service_account_key_path:
            cred = credentials.Certificate(service_account_key_path)
            firebase_admin.initialize_app(cred, options={'databaseURL': database_url})
        else:
            firebase_admin.initialize_app(options={'databaseURL': database_url})

@app.on_event('startup')
def on_startup():
    initialize_firebase(database_url='https://your-database-url.firebaseio.com')

@app.get('/load_data',
         summary='Load data from Firebase Realtime Database',
         description='Loads data from the specified path within Firebase Realtime Database.',
         response_model=List[Document])
async def load_data(path: str, field: str = None, api_key: APIKey = Depends(get_api_key)):
    try:
        from firebase_admin import db
    except ImportError:
        raise HTTPException(status_code=404, detail='firebase_admin package not found')
    ref = db.reference(path)
    data = ref.get()
    documents = []
    if isinstance(data, dict):
        for key in data:
            entry = data[key]
            extra_info = {'document_id': key}
            if isinstance(entry, dict) and field in entry:
                text = entry[field]
            else:
                text = str(entry)
            document = Document(text=text, extra_info=extra_info)
            documents.append(document)
    elif isinstance(data, str):
        documents.append(Document(text=data))
    return documents