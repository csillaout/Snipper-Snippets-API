from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import json
import os
from pydantic import BaseModel
from typing import List


# Load initial data from seedData.json
# Load initial data from seedData.json with error handling
snippets = []
try:
    with open('seedData.json', 'r') as file:
        snippets = json.load(file)
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
except FileNotFoundError as e:
    print(f"File not found: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")



class Snippet(BaseModel):
    language: str
    code: str

class SnippetWithID(Snippet):
    id: int

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/snippets")
def get_all_snippets():
    return JSONResponse(content=snippets)

#snippets get by language
@app.get("/snippets/{language}")
def get_snippets_by_language(language: str):
    # Filter snippets by language
    filtered_snippets = [snippet for snippet in snippets if snippet["language"].lower() == language.lower()]
    if not filtered_snippets:
        raise HTTPException(status_code=404, detail="No snippets found for the specified language")
    return JSONResponse(content=filtered_snippets)

# Get snippet by ID
@app.get("/snippet/{snippet_id}")
def get_snippet_by_id(snippet_id: int):
    # Find the snippet by its ID
    snippet = next((snippet for snippet in snippets if snippet["id"] == snippet_id), None)
    if snippet is None:
        raise HTTPException(status_code=404, detail="Snippet not found")
    return JSONResponse(content=snippet)

# Post new snippet
@app.post("/snippets/", response_model=SnippetWithID)
def create_snippet(snippet: Snippet):
    # Generate the next available ID
    next_id = max(snippet["id"] for snippet in snippets) + 1 if snippets else 1
    new_snippet = {"id": next_id, **snippet.dict()}
    snippets.append(new_snippet)
    
    return new_snippet

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port= 8000)