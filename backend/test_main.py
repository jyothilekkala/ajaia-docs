
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app, Base, get_db


@pytest.fixture
def client():
    # Create an isolated in-memory database for each test.
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
    )

    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


ALICE = {"X-User-Email": "alice@ajaia.test"}
BOB = {"X-User-Email": "bob@ajaia.test"}
UNKNOWN_USER = {"X-User-Email": "unknown@ajaia.test"}


def create_document(client, headers=ALICE, title="Test Document",
                    content="Initial content"):
    response = client.post(
        "/documents",
        headers=headers,
        json={"title": title, "content": content},
    )
    return response


def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Ajaia Docs API is running"


def test_create_and_list_document(client):
    response = create_document(client)

    assert response.status_code == 200
    document_id = response.json()["id"]

    response = client.get("/documents", headers=ALICE)

    assert response.status_code == 200
    assert len(response.json()["owned"]) == 1
    assert response.json()["owned"][0]["id"] == document_id
    assert response.json()["owned"][0]["title"] == "Test Document"
    assert response.json()["shared"] == []


def test_open_and_update_document(client):
    created = create_document(client)
    document_id = created.json()["id"]

    response = client.get(
        f"/documents/{document_id}",
        headers=ALICE,
    )

    assert response.status_code == 200
    assert response.json()["content"] == "Initial content"

    response = client.put(
        f"/documents/{document_id}",
        headers=ALICE,
        json={
            "title": "Updated Document",
            "content": "Updated content",
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Document saved"

    response = client.get(
        f"/documents/{document_id}",
        headers=ALICE,
    )

    assert response.json()["title"] == "Updated Document"
    assert response.json()["content"] == "Updated content"


def test_share_document_with_another_user(client):
    created = create_document(client)
    document_id = created.json()["id"]

    response = client.post(
        f"/documents/{document_id}/share",
        headers=ALICE,
        json={"email": "bob@ajaia.test"},
    )

    assert response.status_code == 200

    response = client.get("/documents", headers=BOB)

    assert response.status_code == 200
    assert len(response.json()["shared"]) == 1
    assert response.json()["shared"][0]["id"] == document_id


def test_shared_user_can_edit_document(client):
    created = create_document(client)
    document_id = created.json()["id"]

    client.post(
        f"/documents/{document_id}/share",
        headers=ALICE,
        json={"email": "bob@ajaia.test"},
    )

    response = client.put(
        f"/documents/{document_id}",
        headers=BOB,
        json={
            "title": "Edited by Bob",
            "content": "Bob's changes",
        },
    )

    assert response.status_code == 200

    response = client.get(
        f"/documents/{document_id}",
        headers=ALICE,
    )

    assert response.json()["title"] == "Edited by Bob"
    assert response.json()["content"] == "Bob's changes"


def test_unshared_user_cannot_access_document(client):
    created = create_document(client)
    document_id = created.json()["id"]

    response = client.get(
        f"/documents/{document_id}",
        headers=BOB,
    )

    assert response.status_code == 403


def test_only_owner_can_share_document(client):
    created = create_document(client)
    document_id = created.json()["id"]

    response = client.post(
        f"/documents/{document_id}/share",
        headers=BOB,
        json={"email": "alice@ajaia.test"},
    )

    assert response.status_code == 403


def test_revoke_document_access(client):
    created = create_document(client)
    document_id = created.json()["id"]

    client.post(
        f"/documents/{document_id}/share",
        headers=ALICE,
        json={"email": "bob@ajaia.test"},
    )

    response = client.delete(
        f"/documents/{document_id}/share",
        headers=ALICE,
        params={"email": "bob@ajaia.test"},
    )

    assert response.status_code == 200

    response = client.get(
        f"/documents/{document_id}",
        headers=BOB,
    )

    assert response.status_code == 403


def test_unknown_user_is_rejected(client):
    response = client.get("/documents", headers=UNKNOWN_USER)
    assert response.status_code == 401


def test_invalid_share_recipient_is_rejected(client):
    created = create_document(client)
    document_id = created.json()["id"]

    response = client.post(
        f"/documents/{document_id}/share",
        headers=ALICE,
        json={"email": "someone@example.com"},
    )

    assert response.status_code == 400


def test_upload_text_file(client):
    response = client.post(
        "/documents/upload",
        headers=ALICE,
        files={
            "file": (
                "notes.txt",
                b"Imported document content",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200
    document_id = response.json()["id"]

    document = client.get(
        f"/documents/{document_id}",
        headers=ALICE,
    )

    assert document.status_code == 200
    assert document.json()["title"] == "notes"
    assert document.json()["content"] == "Imported document content"


def test_upload_markdown_file(client):
    response = client.post(
        "/documents/upload",
        headers=ALICE,
        files={
            "file": (
                "readme.md",
                b"# Project Notes",
                "text/markdown",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "readme"


def test_upload_rejects_unsupported_file(client):
    response = client.post(
        "/documents/upload",
        headers=ALICE,
        files={
            "file": (
                "image.png",
                b"not an image",
                "image/png",
            )
        },
    )

    assert response.status_code == 400


def test_upload_rejects_file_over_2mb(client):
    response = client.post(
        "/documents/upload",
        headers=ALICE,
        files={
            "file": (
                "large.txt",
                b"a" * (2 * 1024 * 1024 + 1),
                "text/plain",
            )
        },
    )

    assert response.status_code == 413


def test_open_nonexistent_document(client):
    response = client.get("/documents/9999", headers=ALICE)
    assert response.status_code == 404
