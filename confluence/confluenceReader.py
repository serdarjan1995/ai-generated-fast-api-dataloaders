from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer, APIKeyHeader
from typing import Optional, List
from pydantic import BaseModel

app = FastAPI()

CONFLUENCE_BASE_URL = '<your_confluence_base_url>'

oauth2_scheme = OAuth2AuthorizationCodeBearer(authorizationUrl='https://auth.atlassian.com', tokenUrl='https://auth.atlassian.com/oauth/token')
api_key_header_auth = APIKeyHeader(name='X-API-Key', auto_error=False)


class Document(BaseModel):
    text: str
    doc_id: str
    extra_info: dict


async def get_api_key(api_key_header: str = Depends(api_key_header_auth)):
    if api_key_header == 'your_api_key_here':
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail='Could not validate credentials')


@app.get('/loadData', response_model=List[Document], summary='Load data from Confluence')
def load_data(space_key: Optional[str] = None,
             page_ids: Optional[List[str]] = None,
             page_status: Optional[str] = None,
             label: Optional[str] = None,
             cql: Optional[str] = None,
             include_attachments: bool = Query(False, description='Include attachments in the results'),
             include_children: bool = Query(False, description='Include page children in the results'),
             start: Optional[int] = None,
             cursor: Optional[str] = None,
             limit: Optional[int] = None,
             max_num_results: Optional[int] = None,
             oauth2: str = Depends(oauth2_scheme),
             api_key: str = Depends(get_api_key)):
    reader = ConfluenceReader(base_url=CONFLUENCE_BASE_URL, oauth2={'token': oauth2}, cloud=True)
    documents = reader.load_data(
        space_key=space_key,
        page_ids=page_ids,
        page_status=page_status,
        label=label,
        cql=cql,
        include_attachments=include_attachments,
        include_children=include_children,
        start=start,
        cursor=cursor,
        limit=limit,
        max_num_results=max_num_results
    )
    return documents


@app.get('/getNextCursor', summary='Get the next cursor from a CQL based search')
def get_next_cursor(api_key: str = Depends(get_api_key)):
    reader = ConfluenceReader(base_url=CONFLUENCE_BASE_URL)
    return {'next_cursor': reader.get_next_cursor()}