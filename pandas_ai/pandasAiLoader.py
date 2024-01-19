from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
import pandas as pd
from pydantic import BaseModel

app = FastAPI()

@app.post('/run_pandas_ai/')
def run_pandas_ai(df: pd.DataFrame, query: str, is_conversational_answer: bool = Query(False, description='Set to False for a parsed output')):
    try:
        from pandasai import PandasAI
        llm = OpenAI()
        pandas_ai = PandasAI(llm)
        result = pandas_ai.run(df, prompt=query, is_conversational_answer=is_conversational_answer)
        return result
    except ImportError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post('/load_data/')
def load_data(df: pd.DataFrame, query: str, is_conversational_answer: bool = Query(False, description='Set to False for a parsed output')):
    try:
        # Logic to load data will be added here following the base.py script.
        pass
    except ImportError as e:
        raise HTTPException(status_code=404, detail=str(e))