from fastapi import FastAPI, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from base import DocugamiReader, Document

app = FastAPI()
security = HTTPBearer()

@app.get('/load_data',
          summary='Load data from Docugami',
          description='Loads nodes in a Document XML Knowledge Graph from Docugami for a set of documents.')
def load_data(docset_id: str,
              document_ids: Optional[List[str]] = None,
              token: HTTPAuthorizationCredentials = Security(security)):
    try:
        reader = DocugamiReader()
        documents = reader.load_data(docset_id=docset_id, document_ids=document_ids, access_token=token.credentials)
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))