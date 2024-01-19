from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyQuery, APIKeyHeader, APIKey
from typing import List
from pydantic import BaseModel

app = FastAPI(title='SharePoint Reader API')

API_KEY = 'secret-api-key'
API_KEY_NAME = 'access_token'
api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def get_api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
):
    if api_key_query == API_KEY:
        return api_key_query
    elif api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=403, detail='Could not validate credentials'
        )

class SharePointFileLoadRequest(BaseModel):
    client_id: str
    client_secret: str
    tenant_id: str
    sharepoint_site_name: str
    sharepoint_folder_path: str
    recursive: bool = False


@app.post('/load-data/', summary='Load Files from SharePoint')
def load_data_from_sharepoint(request: SharePointFileLoadRequest, api_key: APIKey = Security(get_api_key)):
    try:
        loader = SharePointReader(
            client_id=request.client_id,
            client_secret=request.client_secret,
            tenant_id=request.tenant_id
        )
        documents = loader.load_data(
            sharepoint_site_name=request.sharepoint_site_name,
            sharepoint_folder_path=request.sharepoint_folder_path,
            recursive=request.recursive
        )
        return {'documents': documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
