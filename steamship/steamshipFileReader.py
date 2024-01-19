from typing import List, Optional
from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel

app = FastAPI()

api_key_header = APIKeyHeader(name='X-API-Key', auto_error=True)

def get_api_key(api_key_header: str = Security(api_key_header)):
    if not api_key_header:
        raise HTTPException(status_code=403, detail='Could not validate credentials')
    return api_key_header

class Document(BaseModel):
    text: str
    doc_id: Optional[str] = None
    extra_info: dict

class SteamshipFileReader:
    def __init__(self, api_key: Optional[str] = None) -> None:
        if api_key is None:
            raise ValueError('An API key is required to initialize SteamshipFileReader')
        self.api_key = api_key

@app.post('/load_data/', response_model=List[Document])
def load_data(
    workspace: str,
    query: Optional[str] = None,
    file_handles: Optional[List[str]] = None,
    collapse_blocks: Optional[bool] = True,
    join_str: Optional[str] = '\n\n',
    api_key: str = Security(get_api_key)
):
    from steamship import File, Steamship
    client = Steamship(workspace=workspace, api_key=api_key)
    files = []
    if query:
        files_from_query = File.query(client=client, tag_filter_query=query).files
        files.extend(files_from_query)

    if file_handles:
        files.extend([File.get(client=client, handle=h) for h in file_handles])

    docs = []
    for file in files:
        extra_info = {'source': file.handle}
        for tag in file.tags:
            extra_info[tag.kind] = tag.value
        if collapse_blocks:
            text = join_str.join([b.text for b in file.blocks])
            docs.append(Document(text=text, doc_id=file.handle, extra_info=extra_info))
        else:
            docs.extend([Document(text=b.text, doc_id=file.handle, extra_info=extra_info) for b in file.blocks])

    return docs
