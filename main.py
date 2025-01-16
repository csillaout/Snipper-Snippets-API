from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import json
from pydantic import BaseModel
from typing import Optional
from cryptography.fernet import Fernet
import os

print("cryptography library is installed successfully!")

# Path to store the encryption key
key_file_path = 'secret.key'

# Function to load the key from a file
def load_key():
    return open(key_file_path, 'rb').read()

# Function to generate and store the key
def generate_and_store_key():
    key = Fernet.generate_key()
    with open(key_file_path, 'wb') as key_file:
        key_file.write(key)
    return key

# Check if the key file exists
if os.path.exists(key_file_path):
    key = load_key()
else:
    key = generate_and_store_key()

cipher_suite = Fernet(key)

# Load initial data from seedData.json with error handling
snippets = []
file_path = 'seedData.json'
if os.path.exists(file_path):
    try:
        with open(file_path, 'r') as file:
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

class UpdateSnippet(BaseModel):
    language: Optional[str] = None
    code: Optional[str] = None

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/snippets")
def get_all_snippets():
    try:
        decrypted_snippets = []
        for snippet in snippets:
            try:
                decrypted_snippets.append({**snippet, "code": decrypt_text(snippet["code"])})
            except Exception as e:
                print(f"Error decrypting snippet ID {snippet['id']}: {e}")
                raise HTTPException(status_code=500, detail=f"Error decrypting snippet ID {snippet['id']}")
        return JSONResponse(content=decrypted_snippets)
    except Exception as e:
        print(f"Error decrypting snippets: {e}")
        raise HTTPException(status_code=500, detail="Internal server error. Please try again later.")

@app.get("/snippets/{language}")
def get_snippets_by_language(language: str):
    try:
        filtered_snippets = []
        for snippet in snippets:
            if snippet["language"].lower() == language.lower():
                try:
                    filtered_snippets.append({**snippet, "code": decrypt_text(snippet["code"])})
                except Exception as e:
                    print(f"Error decrypting snippet ID {snippet['id']}: {e}")
                    raise HTTPException(status_code=500, detail=f"Error decrypting snippet ID {snippet['id']}")
        if not filtered_snippets:
            raise HTTPException(status_code=404, detail="No snippets found for the specified language")
        return JSONResponse(content=filtered_snippets)
    except Exception as e:
        print(f"Error decrypting snippets: {e}")
        raise HTTPException(status_code=500, detail="Internal server error. Please try again later.")

@app.get("/snippet/{snippet_id}")
def get_snippet_by_id(snippet_id: int):
    try:
        snippet = next((snippet for snippet in snippets if snippet["id"] == snippet_id), None)
        if snippet is None:
            raise HTTPException(status_code=404, detail="Snippet not found")
        try:
            decrypted_snippet = {**snippet, "code": decrypt_text(snippet["code"])}
            return JSONResponse(content=decrypted_snippet)
        except Exception as e:
            print(f"Error decrypting snippet ID {snippet['id']}: {e}")
            raise HTTPException(status_code=500, detail=f"Error decrypting snippet ID {snippet['id']}")
    except Exception as e:
        print(f"Error decrypting snippet: {e}")
        raise HTTPException(status_code=500, detail="Internal server error. Please try again later.")

# function to encrypt text
def encrypt_text(text: str) -> str:
    try:
        encrypted_text = cipher_suite.encrypt(text.encode())
        return encrypted_text.decode()
    except Exception as e:
        print(f"Error encrypting text: {e}")
        raise HTTPException(status_code=500, detail="Error encrypting text.")

# function to decrypt text
def decrypt_text(encrypted_text: str) -> str:
    try:
        decrypted_text = cipher_suite.decrypt(encrypted_text.encode())
        return decrypted_text.decode()
    except Exception as e:
        print(f"Error decrypting text: {e}")
        raise HTTPException(status_code=500, detail="Error decrypting text.")

@app.post("/snippets/", response_model=SnippetWithID)
def create_snippet(snippet: Snippet):
    try:
        # Generate the next available ID
        next_id = max(snippet["id"] for snippet in snippets) + 1 if snippets else 1

        # encrypt the snippet's code
        encrypted_code = encrypt_text(snippet.code)

        new_snippet = {"id": next_id,  "language": snippet.language, 'code': encrypted_code}
        snippets.append(new_snippet)
        
        # Save the newly created snippet to the file
        with open(file_path, 'w') as file:
            json.dump(snippets, file, indent=4)

        return new_snippet
    except Exception as e:
        print(f"Error creating snippet: {e}")
        raise HTTPException(status_code=500, detail="Internal server error. Please try again later.")

@app.delete("/snippets/{language}")
def delete_snippets_by_language(language: str):
    global snippets
    try:
        # filter snippets by language and delete them 
        snippets_to_delete = [snippet for snippet in snippets if snippet["language"].lower() == language.lower()]
        if not snippets_to_delete:
            raise HTTPException(status_code=404, detail="No snippet found")
        snippets = [snippet for snippet in snippets if snippet["language"].lower() != language.lower()]

        # Save the updated snippets to the file
        with open(file_path, 'w') as file:
            json.dump(snippets, file, indent=4)
        
        return snippets_to_delete
    except Exception as e:
        print(f"Error deleting snippets: {e}")
        raise HTTPException(status_code=500, detail="Internal server error. Please try again later.")

@app.put("/snippet/{snippet_id}", response_model=SnippetWithID)
def update_snippet(snippet_id: int, snippet_update: UpdateSnippet):
    try:
        # Find the snippet by its ID
        snippet = next((snippet for snippet in snippets if snippet["id"] == snippet_id), None)
        if snippet is None:
            raise HTTPException(status_code=404, detail="Snippet not found")

        # Update the snippet details
        if snippet_update.language is not None:
            snippet["language"] = snippet_update.language
        if snippet_update.code is not None:
            snippet["code"] = encrypt_text(snippet_update.code)
        
        # Save the updated snippets to the file
        with open(file_path, 'w') as file:
            json.dump(snippets, file, indent=4)
        
        return snippet
    except Exception as e:
        print(f"Error updating snippet: {e}")
        raise HTTPException(status_code=500, detail="Internal server error. Please try again later.")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)