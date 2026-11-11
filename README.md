
# Ajaia Docs

A lightweight collaborative document editor built with React, TypeScript, FastAPI, and SQLite.

Ajaia Docs enables users to create, edit, save, import, and share documents through a clean, intuitive interface.

## Features

- Create, rename, edit, and save documents.
- Rich-text editing with bold, italic, underline, headings, and lists.
- Import TXT and Markdown files.
- Share documents with other demo users.
- View owned documents and documents shared with you.
- Edit shared documents.
- Persistent storage using SQLite.
- Automated backend API tests using pytest.

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Vite |
| Rich-text editor | TipTap |
| Backend | Python, FastAPI |
| Database | SQLite, SQLAlchemy |
| Testing | pytest, FastAPI TestClient |

## Project Structure

```text
ajaia-docs/
├── backend/
│   ├── main.py
│   ├── test_main.py
│   └── ajaia.db
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
└── README.md
```

## Prerequisites

- Python 3.10+
- Node.js and npm

## Getting Started

### 1. Backend Setup

Open a terminal:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy python-multipart pytest httpx
```

### 2. Start the Backend

```bash
uvicorn main:app --reload
```

Backend API: http://127.0.0.1:8000

Interactive API documentation: http://127.0.0.1:8000/docs

### 3. Frontend Setup

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

## Demo Accounts

The application includes two seeded demo identities:

| User | Email |
|---|---|
| Alice | alice@ajaia.test |
| Bob | bob@ajaia.test |

No password is required for the demo.

**Note:** Authentication is simulated using an HTTP request header (`X-User-Email`). This is intended for demonstration purposes and is not production authentication.

## Running Automated Tests

From the backend directory, activate the virtual environment and run:

```bash
pytest -v
```

The automated test suite currently contains 15 tests covering:

- API health check.
- Document creation, listing, retrieval, and updates.
- Document sharing and access control.
- Shared-user editing.
- Access revocation.
- Demo-user validation.
- TXT and Markdown imports.
- Invalid and oversized file uploads.
- Missing document handling.

Tests use an isolated in-memory SQLite database and do not modify the application's local database.

## Database

The application uses SQLite with SQLAlchemy.

The local database is created automatically when the backend starts.

## Limitations

- Demo authentication is simulated and should not be used in production.
- The application does not implement real-time collaborative editing.
- Shared users currently have editing access.
- The application is designed as a lightweight demonstration rather than a production document management platform.
