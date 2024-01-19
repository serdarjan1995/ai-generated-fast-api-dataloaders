from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from llama_hub.youtube_transcript import YoutubeTranscriptReader

app = FastAPI()

@app.get('/transcripts', summary='Fetch transcripts for YouTube videos',
          description='Returns the text transcript of the given YouTube videos.',
          response_model=List[str])
def fetch_transcripts(
ytlinks: List[str] = Query([], description='List of YouTube links', alias='ytlinks'),
languages: List[str] = Query(['en'], description='Preferred languages'),
):
    loader = YoutubeTranscriptReader()
    try:
        documents = loader.load_data(ytlinks=ytlinks, languages=languages)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return [doc.text for doc in documents]

@app.get('/validate_url', summary='Validate YouTube video URL',
          description='Checks if the given URL is a supported YouTube video URL. Returns boolean.',
          response_model=bool)
def validate_url(
url: str = Query(None, description='The YouTube video URL to validate', required=True)
):
    return YoutubeTranscriptReader._extract_video_id(url) is not None