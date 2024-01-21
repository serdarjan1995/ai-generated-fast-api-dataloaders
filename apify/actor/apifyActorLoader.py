from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

from apify_client import ApifyClient

app = FastAPI()

X_API_KEY = APIKeyHeader(name='X-API-Key')


class ActorRunInput(BaseModel):
    actor_id: str
    run_input: Dict
    build: Optional[str] = None
    memory_mbytes: Optional[int] = None
    timeout_secs: Optional[int] = None


@app.post('/load_data/', response_model=List[Dict])
def load_data(
    run_input: ActorRunInput,
    api_key: str = Depends(X_API_KEY)
):
    client = ApifyClient(api_key)
    actor_call = client.actor(run_input.actor_id).call(
        run_input=run_input.run_input,
        build=run_input.build,
        memory_mbytes=run_input.memory_mbytes,
        timeout_secs=run_input.timeout_secs
    )

    dataset_id = actor_call.get('defaultDatasetId')
    if not dataset_id:
        raise HTTPException(status_code=400, detail='Actor run failed or dataset not found.')
    dataset = client.dataset(dataset_id).list_items()

    if 'dataset_mapping_function' not in run_input.run_input:
        raise HTTPException(status_code=400, detail='Dataset mapping function not specified.')

    mapping_function = globals()[run_input.run_input['dataset_mapping_function']]
    documents = list(map(mapping_function, dataset))

    return documents

