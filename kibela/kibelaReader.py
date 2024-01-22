from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
import requests

app = FastAPI(openapi_url="/api/v1/openapi.json")

KIBELA_TEAM_NAME = "KIBELA_TEAM_NAME"
KIBELA_API_URL = f"https://{KIBELA_TEAM_NAME}.kibe.la/api/v1"

KIBELA_TOKEN_HEADER = "access_token"
KIBELA_ACCESS_TOKEN = "KIBELA_ACCESS_TOKEN"
token_header = APIKeyHeader(name=KIBELA_TOKEN_HEADER, auto_error=True)


@app.get("/user")
def get_user(access_token: str = Security(token_header)):
    print(access_token)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(
        KIBELA_API_URL,
        headers=headers,
        data={
            "query": "query KibelaUser {\
                    currentUser {\
                    account\
                    }\
                }"
        },
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Invalid Access Token"
        )
    return response.json()


@app.get("/notes")
def get_notes(access_token: str = Security(token_header)):
    print(access_token)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(
        KIBELA_API_URL,
        headers=headers,
        data={
            "query": "query KibelaNotes {\
            notes(first: 10, orderBy: { field: CONTENT_UPDATED_AT, direction: DESC }) {\
            edges {\
                node {\
                title\
                content\
                publishedAt\
                }\
            }\
            }\
        }"
        },
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Invalid Access Token"
        )
    return response.json()


@app.get("/folders")
def get_folders(access_token: str = Security(token_header)):
    print(access_token)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(
        KIBELA_API_URL,
        headers=headers,
        data={
            "query": "query KibelaFolders {\
            folders(first: 10) {\
                edges {\
                    node {\
                        name\
                    }\
                }\
            }\
        }"
        },
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Invalid Access Token"
        )
    return response.json()


@app.get("/groups")
def get_groups(access_token: str = Security(token_header)):
    print(access_token)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(
        KIBELA_API_URL,
        headers=headers,
        data={
            "query": "query KibelaGroups {\
            groups(first: 10) {\
                edges {\
                    node {\
                        name\
                    }\
                }\
            }\
        }"
        },
    )
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Invalid Access Token"
        )
    return response.json()
