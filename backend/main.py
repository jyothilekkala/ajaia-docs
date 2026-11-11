
import os
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, Header, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session


# DATABASE CONFIGURATION
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ajaia.db")

# Normalize PostgreSQL URLs for psycopg 3
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://", "postgresql+psycopg://", 1
    )
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://", "postgresql+psycopg://", 1
    )

connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


# DATABASE MODELS
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, default="Untitled document")
    content = Column(Text, default="")
    owner = Column(String, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Share(Base):
    __tablename__ = "shares"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    user_email = Column(String, index=True)


Base.metadata.create_all(bind=engine)


# FASTAPI APPLICATION
app = FastAPI(title="Ajaia Docs API")

allowed_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# DATABASE SESSION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# DEMO AUTHENTICATION
def current_user(
    x_user_email: str = Header(default="alice@ajaia.test")
):
    allowed_users = {
        "alice@ajaia.test",
        "bob@ajaia.test"
    }

    if x_user_email not in allowed_users:
        raise HTTPException(status_code=401, detail="Unknown demo user")

    return x_user_email


# ACCESS CONTROL
def accessible_document(document_id, user, db):
    doc = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    shared = db.query(Share).filter_by(
        document_id=document_id,
        user_email=user
    ).first()

    if doc.owner != user and not shared:
        raise HTTPException(status_code=403, detail="Access denied")

    return doc


# REQUEST MODELS
class DocumentInput(BaseModel):
    title: str = "Untitled document"
    content: str = ""


class ShareInput(BaseModel):
    email: str


# HEALTH CHECK
@app.get("/")
def health():
    return {"message": "Ajaia Docs API is running"}


# LIST OWNED AND SHARED DOCUMENTS
@app.get("/documents")
def list_documents(
    user: str = Depends(current_user),
    db: Session = Depends(get_db)
):
    owned = db.query(Document).filter_by(owner=user).all()

    shared_ids = [
        s.document_id
        for s in db.query(Share).filter_by(user_email=user).all()
    ]

    shared = (
        db.query(Document).filter(Document.id.in_(shared_ids)).all()
        if shared_ids else []
    )

    def serialize(doc, is_shared):
        return {
            "id": doc.id,
            "title": doc.title,
            "content": doc.content,
            "owner": doc.owner,
            "shared": is_shared,
            "updated_at": doc.updated_at.isoformat()
        }

    return {
        "owned": [serialize(d, False) for d in owned],
        "shared": [serialize(d, True) for d in shared]
    }


# CREATE DOCUMENT
@app.post("/documents")
def create_document(
    data: DocumentInput,
    user: str = Depends(current_user),
    db: Session = Depends(get_db)
):
    doc = Document(
        title=data.title,
        content=data.content,
        owner=user
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {"id": doc.id, "title": doc.title}


# OPEN DOCUMENT
@app.get("/documents/{document_id}")
def get_document(
    document_id: int,
    user: str = Depends(current_user),
    db: Session = Depends(get_db)
):
    doc = accessible_document(document_id, user, db)

    return {
        "id": doc.id,
        "title": doc.title,
        "content": doc.content,
        "owner": doc.owner
    }


# UPDATE / SAVE DOCUMENT
@app.put("/documents/{document_id}")
def update_document(
    document_id: int,
    data: DocumentInput,
    user: str = Depends(current_user),
    db: Session = Depends(get_db)
):
    doc = accessible_document(document_id, user, db)

    doc.title = data.title
    doc.content = data.content
    doc.updated_at = datetime.utcnow()

    db.commit()

    return {"message": "Document saved"}


# SHARE DOCUMENT
@app.post("/documents/{document_id}/share")
def share_document(
    document_id: int,
    data: ShareInput,
    user: str = Depends(current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter_by(id=document_id).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.owner != user:
        raise HTTPException(status_code=403, detail="Only owner can share")

    if data.email not in {"alice@ajaia.test", "bob@ajaia.test"}:
        raise HTTPException(status_code=400, detail="Use a seeded demo account")

    if data.email == user:
        raise HTTPException(status_code=400, detail="Cannot share with yourself")

    existing = db.query(Share).filter_by(
        document_id=document_id,
        user_email=data.email
    ).first()

    if not existing:
        db.add(Share(document_id=document_id, user_email=data.email))
        db.commit()

    return {"message": f"Shared with {data.email}"}


# REVOKE SHARING
@app.delete("/documents/{document_id}/share")
def revoke_share(
    document_id: int,
    email: str,
    user: str = Depends(current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter_by(id=document_id).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.owner != user:
        raise HTTPException(status_code=403, detail="Only owner can revoke access")

    db.query(Share).filter_by(
        document_id=document_id,
        user_email=email
    ).delete()

    db.commit()

    return {"message": "Access revoked"}


# IMPORT TXT / MARKDOWN FILE
@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    user: str = Depends(current_user),
    db: Session = Depends(get_db)
):
    filename = file.filename or ""

    if not filename.lower().endswith((".txt", ".md")):
        raise HTTPException(
            status_code=400,
            detail="Only TXT and Markdown files are supported"
        )

    raw_content = await file.read()

    if len(raw_content) > 2 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File exceeds 2 MB limit")

    try:
        content = raw_content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must use UTF-8 encoding"
        )

    doc = Document(
        title=filename.rsplit(".", 1)[0],
        content=content,
        owner=user
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {"id": doc.id, "title": doc.title}
