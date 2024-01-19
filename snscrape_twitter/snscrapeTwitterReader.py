from fastapi import FastAPI, HTTPException, Query, Depends, Security
from pydantic import BaseModel
from typing import List, Optional
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader, APIKey
import snscrape.modules.twitter as sntwitter

API_KEY_NAME = 'access_token'
api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)

app = FastAPI()

class Document(BaseModel):
    text: List[str]
    extra_info: dict

def get_api_key(api_key_query: str = Security(api_key_query)):
    if api_key_query == 'SECRET_API_KEY':
        return api_key_query
    else:
        raise HTTPException(status_code=403, detail='Could not validate credentials')

@app.get('/tweets', summary='Fetch tweets from a Twitter profile', responses={200: {'description': 'A list of tweets', 'model': List[Document]}, 400: {'description': 'Invalid parameters'}, 401: {'description': 'Invalid API key'}})
def read_twitter(username: str = Query(..., description='Twitter Username'), num_tweets: int = Query(10, description='Number of tweets to fetch', gt=0), api_key: APIKey = Depends(get_api_key)):
    if num_tweets > 1000:  # Arbitrary limit to avoid overloading
        raise HTTPException(status_code=400, detail='Number of tweets to fetch is too high')
    attributes_container = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f'from:{username}').get_items()):
        if i >= num_tweets:
            break
        attributes_container.append(tweet.rawContent)
    return [Document(text=attributes_container, extra_info={'username': username})]
