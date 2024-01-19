from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
from typing import List, Optional, Tuple
from enum import Enum
from pydantic import BaseModel

from base import GitHubRepositoryIssuesReader, GitHubIssuesClient

app = FastAPI()

X_API_KEY = 'X-Api-Key'
api_key_header = APIKeyHeader(name=X_API_KEY, auto_error=False)


class IssueState(str, Enum):
    OPEN = 'open'
    CLOSED = 'closed'
    ALL = 'all'


class FilterType(str, Enum):
    EXCLUDE = 'exclude'
    INCLUDE = 'include'


class LabelFilter(BaseModel):
    label: str
    filter_type: FilterType


def get_api_key(api_key_header: str = Depends(api_key_header)):
    if api_key_header != 'expected-key':
        raise HTTPException(status_code=403, detail='Could not validate API key')
    return api_key_header


@app.get('/issues', summary='Retrieve GitHub repository issues')
async def get_issues(
    owner: str,
    repo: str,
    state: IssueState = IssueState.OPEN,
    label_filters: Optional[List[LabelFilter]] = None,
    token: str = Depends(get_api_key)
):
    github_client = GitHubIssuesClient(api_token=token)
    reader = GitHubRepositoryIssuesReader(github_client=github_client, owner=owner, repo=repo)
    issues = reader.load_data(state=state, labelFilters=[(lf.label, lf.filter_type) for lf in label_filters] if label_filters else None)
    return issues
