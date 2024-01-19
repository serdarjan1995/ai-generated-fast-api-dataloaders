from typing import List
from fastapi import FastAPI, Query, HTTPException
from base import SECFilingsLoader

app = FastAPI(
    title="SEC Data Downloader",
    description="API to download SEC filings such as 10-K and 10-Q for specified tickers."
)

@app.post('/load_data/', summary='Download SEC filings')
async def load_data(
    tickers: List[str] = Query(..., description='List of ticker symbols'),
    amount: int = Query(..., description='Number of documents to download'),
    filing_type: str = Query(..., description='Type of SEC filing to download', enum=['10-K', '10-Q']),
    num_workers: int = Query(2, description='Number of workers for multithreading/multiprocessing', ge=1),
    include_amends: bool = Query(False, description='Whether to include amended filings')
):
    if not tickers:
        raise HTTPException(status_code=400, detail='Tickers list cannot be empty.')
    loader = SECFilingsLoader(tickers=tickers, amount=amount, filing_type=filing_type, num_workers=num_workers, include_amends=include_amends)
    try:
        loader.load_data()
        return {'status': 'Data loaded successfully'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
