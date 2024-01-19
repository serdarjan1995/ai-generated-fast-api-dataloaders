from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
import requests

class Document(BaseModel):
    text: str

app = FastAPI()

@app.get('/random-joke', summary='Get a Random Dad Joke', response_model=Document, tags=['Dad Jokes'])
async def get_random_dad_joke():
    """Fetch a random dad joke from icanhazdadjoke."""
    try:
        response = requests.get(
            'https://icanhazdadjoke.com/', headers={'Accept': 'application/json'}
        )
        response.raise_for_status()
        json_data = response.json()
        return Document(text=json_data['joke'])
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))
