
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI()
security = HTTPBasic()

class Document(BaseModel):
    text: str
    extra_info: dict
    embedding: Optional[str] = None


class OpensearchReader:
    def __init__(self, host: str, port: int, index: str, basic_auth: Optional[tuple] = None):
        from opensearchpy import OpenSearch
        self._opster_client = OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_compress=True,
            http_auth=basic_auth,
            use_ssl=True,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
        )
        self._index = index

    def load_data(
        self,
        field: str,
        query: Optional[dict] = None,
        embedding_field: Optional[str] = None
    ) -> List[Document]:
        res = self._opster_client.search(body=query, index=self._index)
        documents = []
        for hit in res['hits']['hits']:
            value = hit['_source'][field]
            _ = hit['_source'].pop(field)
            embedding = hit['_source'].get(embedding_field or '', None)
            documents.append(
                Document(text=value, extra_info=hit['_source'], embedding=embedding)
            )
        return documents


@app.get('/load_data',
         summary='Load data from Opensearch index',
         description='Retrieve text fields from documents in an Opensearch index using optional query and embedding field.',
         response_model=List[Document])
def read_opensearch_docs(
    field: str,
    query: Optional[str] = None,
    embedding_field: Optional[str] = None,
    credentials: HTTPBasicCredentials = Depends(security),
    index: str
) -> List[Document]:
    try:
        reader = OpensearchReader(
            host='localhost',
            port=9200,
            index=index,
            basic_auth=(credentials.username, credentials.password)
        )
        return reader.load_data(field, query=query, embedding_field=embedding_field)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
