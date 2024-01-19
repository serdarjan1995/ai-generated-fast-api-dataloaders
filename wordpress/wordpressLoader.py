from typing import List
from fastapi import FastAPI, HTTPException, Query, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import requests
from bs4 import BeautifulSoup

app = FastAPI()
security = HTTPBasic()

@app.get('/load-data', summary='Loads data from Wordpress', response_model=List[dict])
def load_data(credentials: HTTPBasicCredentials = Security(security), url: str = Query(..., description='Base URL of the Wordpress installation'), page: int = Query(1, description='Page number of the posts to load')):
    user = credentials.username
    password = credentials.password

    def get_posts_page(current_page: int):
        response = requests.get(f'{url}/wp-json/wp/v2/posts?per_page=100&page={current_page}', auth=(user, password))
        headers = response.headers
        if 'X-WP-TotalPages' in headers:
            num_pages = int(headers['X-WP-TotalPages'])
        else:
            num_pages = 1
        next_page = current_page + 1 if num_pages > current_page else None
        return {'articles': response.json(), 'next_page': next_page}

    posts = []
    next_page = page

    while next_page is not None:
        resp = get_posts_page(next_page)
        posts.extend(resp['articles'])
        next_page = resp['next_page']

    results = []
    for article in posts:
        body = article.get('content', {}).get('rendered', article.get('content'))
        soup = BeautifulSoup(body, 'html.parser')
        body = soup.get_text()
        title = article.get('title', {}).get('rendered', article.get('title'))
        extra_info = {'id': article['id'], 'title': title, 'url': article['link'], 'updated_at': article['modified']}
        results.append({'text': body, 'extra_info': extra_info})
    return results