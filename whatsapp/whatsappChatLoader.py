from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from typing import List
from pydantic import BaseModel, Field

app = FastAPI()

API_KEY = 'your_api_key'
API_KEY_NAME = 'access_token'
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header != API_KEY:
        raise HTTPException(status_code=403, detail='Could not validate credentials')
    return api_key_header

class Document(BaseModel):
    text: str
    extra_info: dict

class WhatsappChatLoader:
    def __init__(self, path: str):
        self.file_path = path

    def load_data(self) -> List[Document]:
        from chatminer.chatparsers import WhatsAppParser
        path = Path(self.file_path)
        parser = WhatsAppParser(path)
        parser.parse_file()
        df = parser.parsed_messages.get_df()
        docs = []
        for row in df.itertuples():
            extra_info = {
                "source": str(path).split("/")[-1].replace(".txt", ""),
                "author": row.author,
                "timestamp": str(row.timestamp),
            }
            docs.append(
                Document(
                    text=str(row.timestamp) + " " + row.author + ":" + " " + row.message,
                    extra_info=extra_info,
                )
            )
        return docs

@app.post('/load_chat', summary='Load Whatsapp chat data', response_model=List[Document])
def load_chat(path: str = Field(..., description='Path to the Whatsapp chat text file.'), api_key: APIKeyHeader = Depends(get_api_key)):
    loader = WhatsappChatLoader(path=path)
    documents = loader.load_data()
    return documents

whatsapp_loader = WhatsappChatLoader(path='whatsapp.txt')
documents = whatsapp_loader.load_data()

@app.get('/get_documents', summary='Get loaded Whatsapp chat documents', response_model=List[Document])
def get_documents(api_key: APIKeyHeader = Depends(get_api_key)):
    return documents