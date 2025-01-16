# FastAPI Snippet Manager

This is a simple FastAPI application to manage code snippets. The application allows users to create, retrieve, update, and delete code snippets by ID or language.

## Features

- Add a new snippet
- Retrieve all snippets
- Retrieve snippets by language
- Retrieve a snippet by ID
- Update a snippet by ID
- Delete snippets by language

## Endpoints

- `GET /`: Root endpoint that returns a welcome message.
- `GET /snippets`: Retrieve all snippets.
- `GET /snippets/{language}`: Retrieve snippets by language.
- `GET /snippet/{snippet_id}`: Retrieve a snippet by ID.
- `POST /snippets/`: Create a new snippet.
- `PUT /snippet/{snippet_id}`: Update a snippet by ID.
- `DELETE /snippets/{language}`: Delete snippets by language.

## Prerequisites

- Python 3.7+
- `pip` package manager

## Setup

1. Clone the repository:

```sh
git clone https://github.com/your-username/fastapi-snippet-manager.git
cd fastapi-snippet-manager
```

Create a virtual environment and activate it:
python -m venv env
source env/bin/activate # On Windows, use `env\Scripts\activate`

Install the dependencies:
pip install -r requirements.txt

Run the application
uvicorn main:app --reload
