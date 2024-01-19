from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from jira import JIRA

app = FastAPI()

api_key_header = APIKeyHeader(name='api_token', auto_error=False)


class BasicAuth(BaseModel):
    email: str
    api_token: str
    server_url: str


class Oauth2(BaseModel):
    cloud_id: str
    api_token: str


def get_jira_instance(basic_auth: Optional[BasicAuth] = None, oauth: Optional[Oauth2] = None, api_token: str = Security(api_key_header)):
    if oauth:
        options = {
            "server": f"https://api.atlassian.com/ex/jira/{oauth['cloud_id']}",
            "headers": {"Authorization": f"Bearer {api_token}"}
        }
        return JIRA(options=options)
    elif basic_auth:
        return JIRA(
            basic_auth=(basic_auth.email, basic_auth.api_token),
            server=f"https://{basic_auth.server_url}"
        )
    else:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials.")


class Document(BaseModel):
    text: str
    extra_info: dict


@app.post('/load_data', response_model=List[Document])
async def load_data(query: str = Query(..., description='The JQL query string to fetch issues.'), basic_auth: Optional[BasicAuth] = None, oauth: Optional[Oauth2] = None):
    jira = get_jira_instance(basic_auth, oauth)
    try:
        relevant_issues = jira.search_issues(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    issues = []
    for issue in relevant_issues:
        issues.append(
            Document(
                text=f"{issue.fields.summary} \n {issue.fields.description}",
                extra_info={
                    # ... All the issue fields and metadata
                }
            )
        )
    return issues
