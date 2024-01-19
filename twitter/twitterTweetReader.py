from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI()

API_KEY_NAME = 'access_token'
API_KEY_HEADER = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(API_KEY_HEADER)):
    if api_key_header == 'Bearer YOUR_API_SECRET_KEY':
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail='Could not validate credentials')

class Document(BaseModel):
    text: str

class TwitterTweetReader:
    def __init__(self, bearer_token: str, num_tweets: Optional[int] = 100) -> None:
        self.bearer_token = bearer_token
        self.num_tweets = num_tweets

    def load_data(self, twitterhandles: List[str]) -> List[Document]:
        import tweepy

        client = tweepy.Client(bearer_token=self.bearer_token)
        results = []
        for username in twitterhandles:
            user = client.get_user(username=username)
            tweets = client.get_users_tweets(user.data.id, max_results=self.num_tweets)
            response = ''
            for tweet in tweets.data:
                response += tweet.text + '\n'
            results.append(Document(text=response))
        return results

@app.post('/load_tweets/', response_model=List[Document])
async def load_tweets(twitterhandles: List[str], num_tweets: Optional[int] = 100, api_key: APIKey = Security(get_api_key)):
    reader = TwitterTweetReader(bearer_token=api_key, num_tweets=num_tweets)
    return reader.load_data(twitterhandles=twitterhandles)
