
from distutils import file_util
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json
import os
dir = os.path.dirname(__file__)


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/snippet")
def getSnippet():
    
    file = open('seedData.json')
    return json.load(file)

@app.get("/{language}")
def getSnippet(language):
    path = os.path.join(dir, '{fileName}.json'.format(fileName = language))
    file = open()

    return json.load(file)

