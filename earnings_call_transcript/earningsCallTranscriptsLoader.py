from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import uvicorn

app = FastAPI()

class TranscriptRequest(BaseModel):
    year: int
    ticker: str
    quarter: str

@app.post('/transcript/', summary='Fetch Earning Call Transcript')
def get_transcript(request: TranscriptRequest):
    if request.year > datetime.now().year:
        raise HTTPException(status_code=400, detail='The year should be less than the current year')
    if request.quarter not in ['Q1', 'Q2', 'Q3', 'Q4']:
        raise HTTPException(status_code=400, detail='The quarter should be from the list ["Q1","Q2","Q3","Q4"]')
    return EarningsCallTranscript(request.year, request.ticker, request.quarter).load_data()

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)