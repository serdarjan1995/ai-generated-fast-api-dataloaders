from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
import time
import requests

class Document(BaseDataModel):
    text: str
    extra_info: dict

class FeishuDocsReader(BaseModel):
    app_id: str
    app_secret: str
    tenant_access_token: str = ""
    expire: int = 0
    host: str = "https://open.feishu.cn"
    documents_raw_content_url_path: str = "/open-apis/docx/v1/documents/{}/raw_content"
    tenant_access_token_internal_url_path: str = "/open-apis/auth/v3/tenant_access_token/internal"

    def load_data(self, document_ids: List[str]) -> List[Document]:
        results = []
        for document_id in document_ids:
            doc = self._load_doc(document_id)
            results.append(Document(text=doc, extra_info={"document_id": document_id}))
        return results

    def _load_doc(self, document_id: str) -> str:
        url = self.host + self.documents_raw_content_url_path.format(document_id)
        if not self.tenant_access_token or self.expire < time.time():
            self._update_tenant_access_token()
        headers = {'Authorization': f'Bearer {self.tenant_access_token}', 'Content-Type': 'application/json; charset=utf-8',}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()["data"]["content"]

    def _update_tenant_access_token(self):
        url = self.host + self.tenant_access_token_internal_url_path
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        data = {'app_id': self.app_id, 'app_secret': self.app_secret}
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        json_response = response.json()
        self.tenant_access_token = json_response["tenant_access_token"]
        self.expire = time.time() + json_response["expire"]

    def set_lark_domain(self):
        self.host = 'https://open.larksuite.com'

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

@app.post("/token")
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == app_id and form_data.password == app_secret:
        return {'access_token': tenant_access_token, 'token_type': 'bearer'}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect app credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/load", summary="Load document content", description="Load content from document IDs")
async def load_document_content(doc_ids: List[str], token: str = Depends(oauth2_scheme)):
    if token == tenant_access_token:
        reader = FeishuDocsReader(app_id, app_secret)
        return reader.load_data(document_ids=doc_ids)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post("/set-lark-domain", summary="Set domain to Lark", description="Switch the API endpoint to Lark domain")
async def set_lark_domain(token: str = Depends(oauth2_scheme)):
    if token == tenant_access_token:
        reader = FeishuDocsReader(app_id, app_secret)
        reader.set_lark_domain()
        return {'detail': 'Domain switched to Lark'}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )