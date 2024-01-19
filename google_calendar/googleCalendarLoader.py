from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from datetime import date
import os

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

@app.post('/token')
def token(token: str):
    return {'access_token': token}

@app.get('/read_events/', response_model=list)
def read_events(
    number_of_results: Optional[int] = 100,
    start_date: Optional[date] = None,
    token: str = Depends(oauth2_scheme)
):
    credentials = GoogleCalendarReader()._get_credentials()
    if not credentials:
        raise HTTPException(status_code=400, detail='Invalid credentials')
    return GoogleCalendarReader().load_data(
        number_of_results=number_of_results,
        start_date=start_date
    )

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


class GoogleCalendarReader:
    def load_data(self, number_of_results: Optional[int], start_date: Optional[date]):
        from googleapiclient.discovery import build

        credentials = self._get_credentials()
        service = build('calendar', 'v3', credentials=credentials)

        if not start_date:
            start_date = date.today()

        start_datetime_utc = start_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        events_result = (
            service.events()
            .list(
                calendarId='primary',
                timeMin=start_datetime_utc,
                maxResults=number_of_results,
                singleEvents=True,
                orderBy='startTime'
            )
            .execute()
        )

        events = events_result.get('items', [])

        if not events:
            return []

        results = []
        for event in events:
            start_time = event['start'].get('dateTime', event['start'].get('date'))
            end_time = event['end'].get('dateTime', event['end'].get('date'))

            event_string = f"Status: {event['status']}, Summary: {event['summary']}, Start time: {start_time}, End time: {end_time}, "
            organizer = event.get('organizer', {})
            display_name = organizer.get('displayName', 'N/A')
            email = organizer.get('email', 'N/A')
            if display_name != 'N/A':
                event_string += f"Organizer: {display_name} ({email})"
            else:
                event_string += f"Organizer: {email}"
            results.append({'text': event_string})

        return results

    def _get_credentials(self):
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow

        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds