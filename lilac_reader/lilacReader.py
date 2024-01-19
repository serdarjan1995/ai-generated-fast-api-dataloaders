from fastapi import FastAPI, HTTPException, Depends, Query
from typing import List, Optional
from base import LilacReader
from pydantic import BaseModel

app = FastAPI()


class DocumentModel(BaseModel):
    text: str
    doc_id: Optional[str] = None
    extra_info: Optional[dict] = {}


def get_lilac_reader_dependency():
    try:
        return LilacReader()
    except ImportError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/load_data', response_model=List[DocumentModel])
def load_data(
    dataset: str = Query(..., description='The dataset to load, formatted as {namespace}/{dataset_name}'),
    text_path: str = Query('text', description='Path to the text field in the dataset'),
    doc_id_path: Optional[str] = Query(None, description='Path to the document ID field in the dataset'),
    columns: Optional[List[str]] = Query(None, description='Columns to load from the dataset'),
    filters: Optional[List[str]] = Query(None, description='Filters to apply to the dataset before loading'),
    project_dir: Optional[str] = Query(None, description='Lilac project directory to read from'),
    lilac_reader: LilacReader = Depends(get_lilac_reader_dependency)
):
    try:
        documents = lilac_reader.load_data(
            dataset=dataset,
            text_path=text_path,
            doc_id_path=doc_id_path,
            columns=columns,
            filters=filters,
            project_dir=project_dir
        )
        return [DocumentModel(**doc.dict()) for doc in documents]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))