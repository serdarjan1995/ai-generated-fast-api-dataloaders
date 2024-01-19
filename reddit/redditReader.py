from fastapi import FastAPI, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
import os
import praw

app = FastAPI()


class Document(BaseModel):
    text: str


class RedditCreds(BaseModel):
    client_id: str
    client_secret: str
    user_agent: str
    username: str
    password: str


@app.post('/load-data/', summary='Load subreddit data', response_model=List[Document])
async def load_data(subreddits: List[str], search_keys: List[str], post_limit: Optional[int] = 10, creds: RedditCreds = Depends()):
    reddit = praw.Reddit(
        client_id=creds.client_id,
        client_secret=creds.client_secret,
        user_agent=creds.user_agent,
        username=creds.username,
        password=creds.password,
    )

    posts = []
    for sr in subreddits:
        subreddit = reddit.subreddit(sr)
        for kw in search_keys:
            relevant_posts = subreddit.search(kw, limit=post_limit)
            for post in relevant_posts:
                posts.append(Document(text=post.selftext))
                for top_level_comment in post.comments:
                    if isinstance(top_level_comment, praw.models.MoreComments):
                        continue
                    posts.append(Document(text=top_level_comment.body))
    return posts
