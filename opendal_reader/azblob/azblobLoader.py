from fastapi import FastAPI, Depends, HTTPException, Path, Query
from fastapi.security import APIKeyHeader
from typing import List, Optional, Dict
from pydantic import BaseModel

app = FastAPI()

X_API_KEY = APIKeyHeader(name="X-API-Key", auto_error=False)


class Document(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None

class OpendalAzblobReader:
    def __init__(
        self,
        container: str,
        path: str = "/",
        endpoint: str = "",
        account_name: str = "",
        account_key: str = "",
        file_extractor: Optional[Dict[str, Union[str, BaseReader]]] = None,
    ):
        self.path = path
        self.file_extractor = file_extractor
        self.options = {
            "container": container,
            "endpoint": endpoint,
            "account_name": account_name,
            "account_key": account_key,
        }

    def load_data(self) -> List[Document]:
        OpendalReader = download_loader("OpendalReader")
        loader = OpendalReader(
            scheme="azblob",
            path=self.path,
            file_extractor=self.file_extractor,
            **self.options,
        )
        return loader.load_data()


@app.get("/load_data", summary="Loads data from Azure Blob Storage", response_model=List[Document])
async def read_loader(
    container: str = Query(..., description="Name of your Azure Blob container"),
    path: str = Query(..., description="Path of the data to load"),
    endpoint: str = Query(None, description="The endpoint of the Azure Blob service"),
    account_name: str = Query(..., description="Your Azure Blob service account name"),
    account_key: str = Query(..., description="Your Azure Blob service account key"),
    x_api_key: str = Depends(X_API_KEY)
):
    if x_api_key != "expected_api_key":
        raise HTTPException(status_code=403, detail="Invalid API Key")
    loader = OpendalAzblobReader(container, path, endpoint, account_name, account_key)
    return loader.load_data()
