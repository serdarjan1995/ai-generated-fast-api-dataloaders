from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel
from base import DocstringWalker

app = FastAPI(title='DocstringWalker API',
             description='This tool analyzes docstrings from the code without the need to use tokens for the code itself.',
             version='1.0.0',
             openapi_tags=[{'name': 'Docstring Walker', 'description': 'Parse and analyze docstrings from code.'}])

class LoadDataInput(BaseModel):
    code_dir: str
    skip_initpy: Optional[bool] = True
    fail_on_malformed_files: Optional[bool] = False

@app.post('/load_data',
           response_model=list,
           summary='Loads data and docstrings from the specified code directory.',
           tags=['Docstring Walker'])
def load_data(input: LoadDataInput):
    walker = DocstringWalker()
    try:
        docs = walker.load_data(code_dir=input.code_dir,
                                skip_initpy=input.skip_initpy,
                                fail_on_malformed_files=input.fail_on_malformed_files)
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)