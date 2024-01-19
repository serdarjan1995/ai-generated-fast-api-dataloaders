from fastapi import FastAPI, HTTPException, Query, Depends
from typing import Optional, List
from pydantic import BaseModel
import couchdb3

app = FastAPI()

class Document(BaseModel):
    text: str

class SimpleCouchDBReader:
    def __init__(self, user: str, pwd: str, host: str, port: int, couchdb_url: Optional[str] = None, max_docs: int = 1000):
        if couchdb_url is not None:
            self.client = couchdb3.Server(couchdb_url)
        else:
            self.client = couchdb3.Server(f'http://{user}:{pwd}@{host}:{port}')
        self.max_docs = max_docs

    def load_data(self, db_name: str, query: Optional[str] = None) -> List[Document]:
        documents = []
        db = self.client.get(db_name)
        if query is None:
            results = db.view('_all_docs', include_docs=True)
        else:
            query_dict = json.loads(query)
            results = db.find(query_dict)

        if hasattr(results, 'rows'):
            for row in results.rows:
                if 'id' not in row:
                    raise ValueError('`id` field not found in CouchDB document.')
                documents.append(Document(text=json.dumps(row.doc)))
        elif results.get('docs') is not None:
            for item in results.get('docs'):
                if '_id' not in item:
                    raise ValueError('`_id` field not found in CouchDB document.')
                documents.append(Document(text=json.dumps(item)))

        return documents[:self.max_docs]

@app.post('/load_data/', response_model=List[Document], summary='Load documents from CouchDB', description='Fetches documents from a specified CouchDB database based on the provided query.')
def read_couchdb_documents(
    user: str = Query(..., description='Username for CouchDB authentication.'),
    pwd: str = Query(..., description='Password for CouchDB authentication.'),
    host: str = Query(..., description='Host of the CouchDB server.'),
    port: int = Query(..., description='Port number of the CouchDB server.'),
    db_name: str = Query(..., description='Name of the database from which to fetch documents.'),
    query: Optional[str] = Query(None, description='A JSON string representing the query to filter documents in CouchDB.'),
    max_docs: Optional[int] = Query(1000, description='Maximum number of documents to return.')
) -> List[Document]:
    reader = SimpleCouchDBReader(user, pwd, host, port, max_docs=max_docs)
    try:
        return reader.load_data(db_name, query)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
