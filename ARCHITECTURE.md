
# Ajaia Docs — Architecture

## 1. Overview

Ajaia Docs follows a lightweight client-server architecture.

The React frontend provides the document editing experience, while the FastAPI backend exposes REST APIs for document operations, sharing, and file imports. SQLite provides persistent storage.

## 2. High-Level Architecture

```text
              User / Browser
                    |
                    v
          React + TypeScript UI
                    |
                    v
              TipTap Editor
                    |
             HTTP REST Requests
                    |
                    v
              FastAPI Backend
                    |
             SQLAlchemy ORM
                    |
                    v
                SQLite DB
             /            \
        Documents        Shares
```

## 3. Frontend

**Technologies:** React, TypeScript, Vite, TipTap, Lucide React.

Responsibilities:

- Display the document workspace and navigation.
- Create and select documents.
- Provide rich-text editing functionality.
- Automatically save document changes through backend APIs.
- Import TXT and Markdown files.
- Display owned and shared documents.
- Initiate document-sharing operations.

The frontend communicates with the backend using HTTP requests.

## 4. Backend

**Technologies:** Python, FastAPI, SQLAlchemy.

The backend exposes REST endpoints for:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Health check |
| GET | `/documents` | List owned and shared documents |
| POST | `/documents` | Create a document |
| GET | `/documents/{id}` | Retrieve a document |
| PUT | `/documents/{id}` | Update and save a document |
| POST | `/documents/{id}/share` | Share a document |
| DELETE | `/documents/{id}/share` | Revoke sharing access |
| POST | `/documents/upload` | Import TXT or Markdown |

The backend validates requests, enforces document access rules, and persists changes through SQLAlchemy.

## 5. Database Design

SQLite stores application data in two tables.

### Documents

| Field | Description |
|---|---|
| id | Primary key |
| title | Document title |
| content | Document content |
| owner | Owner's demo email |
| updated_at | Last update timestamp |

### Shares

| Field | Description |
|---|---|
| id | Primary key |
| document_id | Reference to the shared document |
| user_email | User receiving access |

A document can have one owner and can be shared with another demo user.

## 6. Document Access and Sharing Flow

1. Alice creates a document.
2. The backend stores the document with Alice as its owner.
3. Alice shares the document with Bob.
4. The backend records the sharing relationship in the Shares table.
5. Bob sees the document under "Shared with me."
6. Bob can open and edit the shared document.
7. Alice can revoke Bob's access.

Only the document owner can grant or revoke access.

## 7. Authentication Approach

For this assignment, authentication is simulated using the `X-User-Email` HTTP header.

The backend accepts two demo identities:

- alice@ajaia.test
- bob@ajaia.test

This keeps the demonstration simple without introducing an external authentication provider.

This mechanism is not intended for production use. A production implementation would require secure authentication, session or token management, and stronger authorization controls.

## 8. File Import

The upload endpoint accepts TXT and Markdown files.

The backend:

1. Validates the file extension.
2. Enforces a 2 MB file-size limit.
3. Decodes file content as UTF-8.
4. Creates a new document using the filename as its title.
5. Persists the imported content in SQLite.

## 9. Testing Strategy

The backend API is tested using pytest and FastAPI TestClient.

The test suite uses an isolated in-memory SQLite database to avoid modifying application data.

The 15 automated tests cover document operations, sharing permissions, user validation, file imports, and error handling.

Run tests using:

```bash
pytest -v
```

## 10. Design Considerations

The implementation prioritizes:

- Simple and maintainable architecture.
- Clear separation between frontend and backend.
- Persistent document storage.
- Explicit access-control checks.
- Minimal external dependencies.
- Automated validation of core backend behavior.

Real-time multi-user editing, production authentication, and advanced document history are intentionally outside the scope of this implementation.
