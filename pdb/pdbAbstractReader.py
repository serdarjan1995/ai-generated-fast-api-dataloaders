from fastapi import FastAPI, HTTPException, Query
from typing import List
from fastapi.security.api_key import APIKeyHeader
from llama_hub.pdb.utils import get_pdb_abstract
from llama_index.readers.schema.base import Document

app = FastAPI()

API_KEY_NAME = 'access_token'
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


@app.get('/read-abstracts', summary='Fetch abstracts for PDB entries', response_model=List[Document])
async def read_abstracts(
    pdb_ids: List[str] = Query(..., description='List of PDB IDs to fetch the abstracts for'),
    api_key: str = Depends(api_key_header)):
    if api_key != 'your_api_key':
        raise HTTPException(status_code=403, detail='Could not validate credentials')
    results = []
    for pdb_id in pdb_ids:
        title, abstracts = get_pdb_abstract(pdb_id)
        primary_citation = abstracts[title]
        abstract = primary_citation['abstract']
        abstract_text = '\n'.join(
            ['\n'.join([str(k), str(v)]) for k, v in abstract.items()]
        )
        results.append(
            Document(
                text=abstract_text,
                extra_info={'pdb_id': pdb_id, 'primary_citation': primary_citation},
            )
        )
    return results
