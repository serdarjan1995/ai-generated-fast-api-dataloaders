from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from typing import List
from pydantic import BaseModel
import gkeepapi

app = FastAPI()

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class Document(BaseModel):
    text: str
    extra_info: dict


def get_keep(username: str, password: str) -> gkeepapi.Keep:
    keep = gkeepapi.Keep()
    success = keep.login(username, password)
    if not success:
        raise RuntimeError("Failed to login to Google Keep.")
    return keep


@app.post("/load_data/", response_model=List[Document])
async def load_data(document_ids: List[str], username: str, password: str, token: str = Security(api_key_header)):
    if token != "expected_token_value":
        raise HTTPException(status_code=403, detail="Invalid API Key")
    keep = get_keep(username, password)
    results = []
    for note_id in document_ids:
        note = keep.get(note_id)
        if note is None:
            raise HTTPException(status_code=404, detail=f"Note with id {note_id} not found.")
        text = f"Title: {note.title}\nContent: {note.text}"
        results.append(Document(text=text, extra_info={"note_id": note_id}))
    return results


@app.post("/load_all_notes/", response_model=List[Document])
async def load_all_notes(username: str, password: str, token: str = Security(api_key_header)):
    if token != "expected_token_value":
        raise HTTPException(status_code=403, detail="Invalid API Key")
    keep = get_keep(username, password)
    notes = keep.all()
    results = []
    for note in notes:
        text = f"Title: {note.title}\nContent: {note.text}"
        results.append(Document(text=text, extra_info={"note_id": note.id}))
    return results