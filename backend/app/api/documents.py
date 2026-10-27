import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_hr_admin
from app.core.config import BASE_DIR, settings
from app.core.database import get_db
from app.models.document import AccessLevel, Document
from app.models.user import User, UserRole
from app.schemas.document import DocumentRead
from app.services.pdf_processor import PDFProcessingError, process_pdf
from app.services.vector_store import delete_document_chunks, index_chunks

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = BASE_DIR / settings.upload_dir
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    title: str | None = Form(None),
    access_level: AccessLevel = Form(AccessLevel.GENERAL),
    db: Session = Depends(get_db),
    admin: User = Depends(require_hr_admin),
):
    original_name = file.filename or "document.pdf"
    if not original_name.lower().endswith(".pdf"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only PDF files are allowed")

    # Read at most limit + 1 bytes, so huge files can't fill memory
    max_bytes = settings.max_upload_mb * 1024 * 1024
    content = file.file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            f"File is larger than {settings.max_upload_mb} MB",
        )
    if not content.startswith(b"%PDF"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "File content is not a real PDF")

    stored_name = f"{uuid.uuid4().hex}.pdf"
    path: Path = UPLOAD_DIR / stored_name
    path.write_bytes(content)

    try:
        page_count, chunks = process_pdf(path)
    except PDFProcessingError as exc:
        path.unlink(missing_ok=True)  # don't keep unusable files
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc))

    document = Document(
        title=(title or Path(original_name).stem).strip(),
        original_filename=original_name,
        stored_filename=stored_name,
        access_level=access_level.value,
        page_count=page_count,
        chunk_count=len(chunks),
        uploaded_by=admin.id,
    )
    db.add(document)
    db.flush()  # assigns document.id without saving permanently yet

    try:
        index_chunks(document.id, document.title, document.access_level, chunks)
    except Exception:
        # Indexing failed: undo everything so the two stores never disagree
        db.rollback()
        delete_document_chunks(document.id)
        path.unlink(missing_ok=True)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Document could not be indexed. Please try again.",
        )

    db.commit()
    db.refresh(document)
    return document


@router.get("", response_model=list[DocumentRead])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Document).order_by(Document.id)
    # Employees only see General documents
    if current_user.role != UserRole.HR_ADMIN.value:
        query = query.where(Document.access_level == AccessLevel.GENERAL.value)
    return db.scalars(query).all()


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_hr_admin),
):
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")

    delete_document_chunks(document.id)  # remove vectors first
    (UPLOAD_DIR / document.stored_filename).unlink(missing_ok=True)
    db.delete(document)
    db.commit()