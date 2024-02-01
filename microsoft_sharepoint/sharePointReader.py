from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyQuery, APIKeyHeader, APIKey
from typing import List
from pydantic import BaseModel
import llama_hub.microsoft_sharepoint as SharePointReader

app = FastAPI(title="SharePoint Reader API", openapi_url="/api/v1/openapi.json")


class SharePointFileLoadRequest(BaseModel):
    client_id: str
    client_secret: str
    tenant_id: str
    sharepoint_site_name: str
    sharepoint_folder_path: str
    recursive: bool = False


@app.post("/load-data/", summary="Load Files from SharePoint")
def load_data_from_sharepoint(request: SharePointFileLoadRequest):
    try:
        loader = SharePointReader(
            client_id=request.client_id,
            client_secret=request.client_secret,
            tenant_id=request.tenant_id,
        )
        documents = loader.load_data(
            sharepoint_site_name=request.sharepoint_site_name,
            sharepoint_folder_path=request.sharepoint_folder_path,
            recursive=request.recursive,
        )
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
