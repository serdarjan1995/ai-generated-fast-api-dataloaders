from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI(title='Rayyan Reader API', version='1.0.0')


class Document(BaseModel):
    text: str
    extra_info: dict


class RayyanReader:
    def __init__(self, rayyan_url: str = 'https://rayyan.ai'):
        from rayyan import Rayyan
        from rayyan.user import User
        self.rayyan = Rayyan(url=rayyan_url)
        user = User(self.rayyan).get_info()

    def load_data(self, review_id: str, filters: Optional[dict] = None) -> List[Document]:
        from rayyan.review import Review
        rayyan_review = Review(self.rayyan)
        my_review = rayyan_review.get(review_id)
        if filters is None:
            filters = {}
        result_params = {'start': 0, 'length': 100}
        result_params.update(filters)
        review_results = rayyan_review.results(review_id, result_params)
        articles = review_results['data']
        return [Document(text=article['body'], extra_info=article) for article in articles]

rayyan_reader = RayyanReader()

@app.get('/load_data', summary='Load articles from a review', response_model=List[Document])
async def get_load_data(review_id: str = Query(..., description='Rayyan review ID'), filters: Optional[str] = Query(None, description='Filters to apply to the review')):
    try:
        return rayyan_reader.load_data(review_id, filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))