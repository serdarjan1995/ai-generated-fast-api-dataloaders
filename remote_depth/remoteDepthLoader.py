from fastapi import FastAPI, HTTPException
from typing import List, Optional
from base import RemoteDepthReader

app = FastAPI()

@app.post('/load', summary='Load documents from a URL with depth.',
         description='Load and parse documents and links from given URL according to specified depth.')
def load_url(url: str, depth: int = 1, domain_lock: bool = False):
    try:
        loader = RemoteDepthReader(depth=depth, domain_lock=domain_lock)
        documents = loader.load_data(url=url)
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/health', summary='API health check',
         description='Check if the API is running.')
def health_check():
    return {'status': 'running'}
