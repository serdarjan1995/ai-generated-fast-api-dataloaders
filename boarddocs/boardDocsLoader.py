from typing import List, Optional
from fastapi import FastAPI, HTTPException, status, Query, Security, Depends
from fastapi.security.api_key import APIKeyQuery, APIKey
from pydantic import BaseModel
import json
import requests
from bs4 import BeautifulSoup
import html2text

app = FastAPI()

API_KEY_NAME = 'access_token'
api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)


async def get_api_key(
    api_key_query: str = Security(api_key_query),
):
    if api_key_query == 'SECURE_API_KEY':
        return api_key_query
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='Could not validate credentials'
        )

class Document(BaseModel):
    text: str
    doc_id: str
    extra_info: dict

class BoardDocsReader:
    def __init__(self, site: str, committee_id: str) -> None:
        self.site = site
        self.committee_id = committee_id
        self.base_url = 'https://go.boarddocs.com/' + site + '/Board.nsf'
        self.headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'sec-ch-ua': ('\"Google Chrome\";v=\"113\", \"Chromium\";v=\"113\", \"Not-A.Brand\";v=\"24\"'),
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '\"macOS\"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-requested-with': 'XMLHttpRequest',
        }

    def get_meeting_list(self) -> List[dict]:
        meeting_list_url = self.base_url + '/BD-GetMeetingsList?open'
        data = 'current_committee_id=' + self.committee_id
        response = requests.post(meeting_list_url, headers=self.headers, data=data)
        meetingsData = json.loads(response.text)
        meetings = [
            {
                'meetingID': meeting.get('unique', None),
                'date': meeting.get('numberdate', None),
                'unid': meeting.get('unid', None),
            }
            for meeting in meetingsData
        ]
        return meetings

    def process_meeting(self, meeting_id: str, index_pdfs: bool = True) -> List[Document]:
        agenda_url = self.base_url + '/PRINT-AgendaDetailed'
        data = 'id=' + meeting_id + '&' + 'current_committee_id=' + self.committee_id
        response = requests.post(agenda_url, headers=self.headers, data=data)
        soup = BeautifulSoup(response.content, 'html.parser')
        agenda_date = soup.find('div', {'class': 'print-meeting-date'}).string
        agenda_title = soup.find('div', {'class': 'print-meeting-name'}).string
        agenda_data = html2text.html2text(response.text)
        docs = []
        agenda_doc = Document(
            text=agenda_data,
            doc_id=meeting_id,
            extra_info={
                'committee': self.committee_id,
                'title': agenda_title,
                'date': agenda_date,
                'url': agenda_url,
            },
        )
        docs.append(agenda_doc)
        return docs

    def load_data(self, meeting_ids: Optional[List[str]] = None) -> List[Document]:
        if not meeting_ids:
            meeting_ids = [
                meeting.get('meetingID') for meeting in self.get_meeting_list()
            ]
        docs = []
        for meeting_id in meeting_ids:
            docs.extend(self.process_meeting(meeting_id))
        return docs

board_docs_reader_instance = BoardDocsReader(site='ca/redwood', committee_id='A4EP6J588C05')

@app.get('/meeting-list', summary='Retrieve meeting list', response_model=List[dict])
async def get_meeting_list(api_key: APIKey = Depends(get_api_key)):
    try:
        return board_docs_reader_instance.get_meeting_list()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get('/process-meeting/{meeting_id}', summary='Retrieve documents from a meeting')
async def process_meeting(meeting_id: str, api_key: APIKey = Depends(get_api_key)):
    try:
        return board_docs_reader_instance.process_meeting(meeting_id=meeting_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get('/load-data', summary='Load all meetings and documents')
async def load_data(meeting_ids: Optional[List[str]] = Query(None), api_key: APIKey = Depends(get_api_key)):
    try:
        return board_docs_reader_instance.load_data(meeting_ids=meeting_ids)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
