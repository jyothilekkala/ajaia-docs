# Ajaia Docs – Submission

## Project Overview

Ajaia Docs is a lightweight document management application that allows users to create, edit, format, save, reopen, and share documents.

## Application Links

- **Live Application:** https://ajaia-docs-taupe-iota.vercel.app/
- **Backend API:** https://ajaia-docs-api-z4l9.onrender.com/
- **GitHub Repository:** https://github.com/jyothilekkala/ajaia-docs
- **Demo Video:** [Add your Zoom recording's YouTube URL here]

## Demo Accounts

The application includes two demo users:

| Display Name | Login Email |
|---|---|
| Jyothi | alice@ajaia.test |
| Pavan | bob@ajaia.test |

Use these accounts to demonstrate document ownership and sharing.

## Features Implemented

- Create and manage documents.
- Rename existing documents.
- Rich-text editing with bold, italic, underline, and headings.
- Bulleted and numbered lists.
- Save documents and reopen them.
- Import TXT and Markdown files.
- Share documents with another user.
- Distinguish owned documents from shared documents.
- Persist documents across page refreshes.

## Technology Stack

**Frontend**
- React
- TypeScript
- Vite
- TipTap rich-text editor

**Backend**
- Python
- FastAPI
- SQLAlchemy

**Database**
- SQLite for local development
- Neon PostgreSQL for deployed application

**Deployment**
- Vercel – Frontend
- Render – Backend

## Running Locally

### Backend

```bash
cd backend

python -m venv venv

# Windows:
venv\Scripts\activate

# Linux / WSL:
source venv/bin/activate

pip install -r requirements.txt

python -m uvicorn main:app --reload
```

Backend API documentation:

http://127.0.0.1:8000/docs

### Frontend

Open another terminal:

```bash
cd frontend

npm install

npm run dev
```

Open:

http://localhost:5173/

## Validation and Testing

- Backend automated tests: **15 passed**
- Frontend production build: `npm run build` completed successfully.
- Tested document creation, editing, persistence, and sharing workflows.

## Architecture

The React frontend communicates with the FastAPI backend through REST API endpoints. The backend uses SQLAlchemy to interact with the database. The deployed application uses Neon PostgreSQL for persistent storage.

## AI Workflow

AI assistance was used during development for implementation guidance, debugging, test development, documentation, and troubleshooting.

The development process included reviewing generated suggestions, integrating relevant changes, running automated tests, and validating the frontend production build.

## Known Scope Limitations

This project focuses on core document management and sharing functionality. It does not implement real-time collaborative editing or simultaneous live cursor updates.

