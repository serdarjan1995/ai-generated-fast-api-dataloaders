from typing import List, Optional
from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from base import DiscordReader, Document

app = FastAPI(title='Discord Loader', description='FastAPI application for loading conversations from Discord channels')

api_key_header = APIKeyHeader(name='Authorization', auto_error=False)


class ChannelData(BaseModel):
    channel_ids: List[int]
    limit: Optional[int] = None
    oldest_first: bool = True


@app.post('/load_data/', summary='Load data from Discord channels',
           description='Loads conversations from Discord channels specified by the user.')
async def load_data_from_discord(
        channel_data: ChannelData,
        api_key: str = Security(api_key_header)
):
    if api_key is None:
        raise HTTPException(status_code=403, detail='API Key required')
    discord_reader = DiscordReader(discord_token=api_key)
    try:
        documents = discord_reader.load_data(channel_ids=channel_data.channel_ids, limit=channel_data.limit, oldest_first=channel_data.oldest_first)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {'documents': [doc.dict() for doc in documents]}


@app.get('/', summary='Index', description='Root endpoint')
async def read_index():
    return {'message': 'Welcome to the Discord Loader API!'}
