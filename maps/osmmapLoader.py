from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional
from base import OpenMap, Document

app = FastAPI()

@app.get('/load_data', summary='Load map data for a specified area.', response_model=List[Document])
def load_data(
    localarea: str = Query(..., description='Area or location you are searching for', max_length=100),
    search_tag: str = Query(None, description='Tag that you are looking for'),
    remove_keys: List[str] = Query(['nodes', 'geometry', 'members'], description='List of keys that need to be removed from the response'),
    tag_only: bool = Query(True, description='Return the nodes that have tags if True, otherwise return all nodes'),
    tag_values: List[str] = Query([], description='Filters for the given area'),
    local_area_buffer: int = Query(2000, description='Range that you wish to cover in meters'),
    key: Optional[str] = Query(None, description='Your access key or token, if applicable')
) -> List[Document]:
    loader = OpenMap()
    try:
        documents = loader.load_data(
            localarea=localarea,
            search_tag=search_tag,
            tag_only=tag_only,
            remove_keys=remove_keys,
            tag_values=tag_values,
            local_area_buffer=local_area_buffer
        )
        return documents
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
