
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security.api_key import APIKeyQuery, APIKeyHeader, APIKey
from fastapi.openapi.models import APIKeyIn

from pydantic import BaseModel
from slack_sdk import WebClient
import os
import logging

# Initialize FastAPI application
app = FastAPI()

# Security schemes for token authentication
API_KEY_NAME = 'access_token'
API_KEY = os.getenv('SLACK_BOT_TOKEN', 'your_api_key_here')
api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def get_api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
):
    if api_key_query == API_KEY:
        return api_key_query
    elif api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='Could not validate credentials'
        )


class SlackReader:
    def __init__(
        self,
        slack_token: str,
        earliest_date: Optional[datetime] = None,
        latest_date: Optional[datetime] = None,
        workspace_url: Optional[str] = '',
    ):
        self.client = WebClient(token=slack_token)
        self.workspace_url = workspace_url
        if earliest_date:
            self.earliest_date_timestamp = earliest_date.timestamp()
            self.latest_date_timestamp = (
                latest_date.timestamp() if latest_date else datetime.now().timestamp()
            )
        else:
            self.earliest_date_timestamp = None

        res = self.client.api_test()
        if not res['ok']:
            raise ValueError(f'Error initializing Slack API: {res['error']}')

    # Method definitions would be here. _read_message and _read_channel are omitted for brevity.
    def load_data(
        self, channel_ids: List[str], reverse_chronological: bool = True
    ):
        # Method implementation is omitted for brevity.
        pass


class Document(BaseModel):
    text: str
    extra_info: dict


@app.post('/load', summary='Load messages from Slack channel')
def load_slack_data(
    channel_ids: List[str],
    reverse_chronological: Optional[bool] = True,
    earliest_date: Optional[datetime] = None,
    latest_date: Optional[datetime] = None,
    workspace_url: Optional[str] = None,
    key: APIKey = Depends(get_api_key)
):
    try:
        slack_reader = SlackReader(key, earliest_date, latest_date, workspace_url)
        documents = slack_reader.load_data(
            channel_ids=channel_ids, reverse_chronological=reverse_chronological
        )
        return {'documents': documents}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get('/')
async def root():
    return {'message': 'Welcome to the Slack Loader API'}
    