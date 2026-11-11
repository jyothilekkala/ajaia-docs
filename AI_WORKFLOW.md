
# Ajaia Docs — AI Development Workflow

## 1. Overview

AI assistance was used throughout the development of Ajaia Docs to accelerate implementation, troubleshoot issues, review design decisions, and improve code quality.

The development process remained iterative, with implementation decisions and application behavior validated locally.

## 2. Areas Where AI Assistance Was Used

### Architecture and Technology Selection

AI assistance helped evaluate a lightweight architecture using:

- React and TypeScript for the frontend.
- TipTap for rich-text editing.
- FastAPI for backend REST APIs.
- SQLite and SQLAlchemy for persistence.
- pytest for backend testing.

The focus was to meet the assignment requirements without introducing unnecessary infrastructure or paid services.

### Frontend Development

AI assistance supported:

- Integrating TipTap with React.
- Implementing rich-text formatting controls.
- Connecting document operations to backend APIs.
- Troubleshooting frontend build and runtime issues.
- Refining interface labels and interaction behavior.

### Backend Development

AI assistance supported:

- Designing document and sharing data models.
- Implementing REST endpoints.
- Adding document access checks.
- Implementing TXT and Markdown imports.
- Handling invalid requests and upload-size limits.

### Debugging and Validation

AI assistance helped investigate issues by reviewing terminal output, API responses, and frontend behavior.

Changes were applied incrementally and checked in the local development environment.

### Automated Testing

AI assistance helped create a pytest suite using FastAPI TestClient and an isolated in-memory SQLite database.

The final test run completed successfully:

**15 passed, 0 failed.**

## 3. Development Workflow

The workflow followed an iterative approach:

1. Define the application requirements.
2. Establish the frontend and backend structure.
3. Implement core functionality incrementally.
4. Connect frontend operations to backend APIs.
5. Run the application and validate user workflows.
6. Investigate and fix issues using error output.
7. Add automated backend tests.
8. Document architecture, setup, and validation.

## 4. Human Review and Validation

AI-generated suggestions were reviewed and adapted to the existing project structure.

The application was manually exercised to verify:

- Document creation and editing.
- Persistence after refreshing the browser.
- Rich-text formatting.
- TXT and Markdown imports.
- Sharing between Alice and Bob.
- Editing shared documents.
- Access revocation.

Backend behavior was additionally validated through the automated test suite.

## 5. Responsible AI Usage

AI was used as a development assistant rather than as a replacement for testing or engineering judgment.

The implementation was checked against actual application behavior, and the final code was validated locally.

Known limitations, including simulated authentication and the absence of real-time collaboration, are documented separately.
