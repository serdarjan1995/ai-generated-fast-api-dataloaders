from fastapi import FastAPI, Query, HTTPException
from typing import Optional
from base import IMDBReviews

app = FastAPI()

@app.get('/load-reviews/', summary='Load IMDB movie reviews')
async def load_movie_reviews(
    movie_name_year: str = Query(..., description='The name of the movie or series and year, e.g., "The Social Network 2010"'),
    webdriver_engine: str = Query('google', enum=['google', 'edge', 'firefox'], description='The webdriver engine to use'),
    generate_csv: Optional[bool] = Query(False, description='Whether to generate a CSV file or not'),
    multithreading: Optional[bool] = Query(False, description='Whether to use multithreading or not'),
    max_workers: int = Query(0, description='The number of workers to use if multithreading is enabled'),
    reviews_folder: str = Query('movie_reviews', description='The folder path to save the reviews')
):
    try:
        imdb_reviews = IMDBReviews(
            movie_name_year,
            webdriver_engine,
            generate_csv,
            multithreading,
            max_workers,
            reviews_folder
        )
        return imdb_reviews.load_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))