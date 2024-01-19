from typing import List
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel

app = FastAPI()

api_key_header = APIKeyHeader(name='Authorization', auto_error=False)


class Document(BaseModel):
    text: str
    extra_info: dict


def get_api_key(
    api_key_header: str = Security(api_key_header),
):
    if api_key_header is None:
        raise HTTPException(status_code=403, detail='Could not validate credentials')
    return api_key_header


@app.get('/read_hubspot_data', response_model=List[Document], summary='Load Hubspot Data', description='Load Hubspot data including deals, contacts, and companies.')
def read_hubspot_data(token: str = Depends(get_api_key)):
    from hubspot import HubSpot
    api_client = HubSpot(access_token=token)
    all_deals = api_client.crm.deals.get_all()
    all_contacts = api_client.crm.contacts.get_all()
    all_companies = api_client.crm.companies.get_all()
    results = [
        Document(
            text=str(all_deals).replace('\n', ''), extra_info={'type': 'deals'}
        ),
        Document(
            text=str(all_contacts).replace('\n', ''), extra_info={'type': 'contacts'}
        ),
        Document(
            text=str(all_companies).replace('\n', ''), extra_info={'type': 'companies'}
        ),
    ]
    return results