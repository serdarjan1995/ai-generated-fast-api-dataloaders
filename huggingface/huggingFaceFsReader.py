from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from typing import List
from pydantic import BaseModel
import json

"""Hugging Face file reader.

A parser for HF files.

"""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, List

import pandas as pd
from llama_index.readers.base import BaseReader
from llama_index.readers.schema.base import Document


class HuggingFaceFSReader(BaseReader):
    r"""Hugging Face File System reader.

    Uses the new Filesystem API from the Hugging Face Hub client library.

    Args:


    """

    def __init__(self) -> None:
        from huggingface_hub import HfFileSystem

        self.fs = HfFileSystem()

    def load_dicts(self, path: str) -> List[Dict]:
        """Parse file."""

        test_data = self.fs.read_bytes(path)

        path = Path(path)
        if ".gz" in path.suffixes:
            import gzip

            with TemporaryDirectory() as tmp:
                tmp = Path(tmp)
                with open(tmp / "tmp.jsonl.gz", "wb") as fp:
                    fp.write(test_data)

                f = gzip.open(tmp / "tmp.jsonl.gz", "rb")
                raw = f.read()
                data = raw.decode()
        else:
            data = test_data.decode()

        text_lines = data.split("\n")
        json_dicts = []
        for t in text_lines:
            try:
                json_dict = json.loads(t)
            except json.decoder.JSONDecodeError:
                continue
            json_dicts.append(json_dict)
        return json_dicts

    def load_df(self, path: str) -> pd.DataFrame:
        """Load pandas dataframe."""
        return pd.DataFrame(self.load_dicts(path))

    def load_data(self, path: str) -> List[Document]:
        """Load data."""
        json_dicts = self.load_dicts(path)
        docs = []
        for d in json_dicts:
            docs.append(Document(text=str(d)))
        return docs


app = FastAPI(openapi_url="/api/v1/openapi.json")
api_key_header = APIKeyHeader(name="access_token", auto_error=False)


class Document(BaseModel):
    text: str


class ErrorModel(BaseModel):
    detail: str


@app.get(
    "/load-dicts",
    summary="Load JSON dictionaries",
    response_model=List[dict],
    responses={404: {"model": ErrorModel}},
)
def get_load_dicts(path: str, api_key: str = Security(api_key_header)):
    try:
        reader = HuggingFaceFSReader()
        return reader.load_dicts(path)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get(
    "/load-df",
    summary="Load a pandas DataFrame",
    response_model=List[dict],
    responses={404: {"model": ErrorModel}},
)
def get_load_df(path: str, api_key: str = Security(api_key_header)):
    try:
        reader = HuggingFaceFSReader()
        df = reader.load_df(path)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get(
    "/load-data",
    summary="Load documents",
    response_model=List[Document],
    responses={404: {"model": ErrorModel}},
)
def get_load_data(path: str, api_key: str = Security(api_key_header)):
    try:
        reader = HuggingFaceFSReader()
        docs = reader.load_data(path)
        return [{"text": doc.text} for doc in docs]
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
