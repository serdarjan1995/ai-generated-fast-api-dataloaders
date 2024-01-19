from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from base import StripeDocsReader

app = FastAPI()


@app.get('/load_data/', summary='Load data from Stripe Documentation', description='Load and return data asynchronously from Stripe Docs sitemap.')
async def load_data(html_to_text: Optional[bool] = Query(False, description='Convert HTML to text'),
                   limit: Optional[int] = Query(10, description='Maximum number of concurrent requests'),
                   filters: Optional[List[str]] = Query(['/docs'], description='Filters to scope the docs')):
    try:
        loader = StripeDocsReader(html_to_text=html_to_text, limit=limit)
        documents = loader.load_data(filters=filters)
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
