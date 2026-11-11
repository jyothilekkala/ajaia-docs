
# Ajaia Docs — Submission Guide

## Project Overview

Ajaia Docs is a lightweight collaborative document editor built using React, TypeScript, FastAPI, and SQLite.

The application supports document creation, rich-text editing, persistent storage, file imports, and document sharing between demo users.

## Key Features

- Create, rename, edit, and save documents.
- Rich-text formatting using TipTap.
- Import TXT and Markdown files.
- Share documents between Alice and Bob.
- View owned and shared documents separately.
- Edit shared documents.
- Persistent storage using SQLite.

## Technology Stack

- React
- TypeScript
- Vite
- TipTap
- Python
- FastAPI
- SQLAlchemy
- SQLite
- pytest

## Running the Application

Refer to `README.md` for complete setup instructions.

Frontend: http://localhost:5173

Backend API: http://127.0.0.1:8000

API documentation: http://127.0.0.1:8000/docs

## Demo Accounts

| User | Email |
|---|---|
| Jyothi | alice@ajaia.test |
| Pavan | bob@ajaia.test |

The demo uses simulated identity headers. No passwords are required.

## Automated Testing

Run the backend tests from the backend directory:

```bash
pytest -v
```

Latest validation: **15 tests passed.**

Tests use an isolated in-memory SQLite database.

## Documentation

- `README.md` — Setup, installation, and usage.
- `ARCHITECTURE.md` — System architecture and design.
- `AI_WORKFLOW.md` — AI-assisted development workflow.
- `SUBMISSION.md` — Submission and reviewer guide.

## Known Limitations

- Authentication is simulated for demonstration purposes.
- Real-time collaborative editing is not implemented.
- Shared users currently have editing access.
- Document history and version restoration are not implemented.

## Deliverables

- Application source code.
- Backend automated tests.
- Architecture documentation.
- AI workflow documentation.
- Setup and submission instructions.
- Application walkthrough video and screenshots (to be added).
- Live application URL (to be added, if deployment is completed).
