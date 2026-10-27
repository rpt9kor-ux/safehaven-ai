import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select  # noqa: E402

from app import models  # noqa: E402,F401
from app.core.config import BASE_DIR, settings  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402
from app.models.document import Document  # noqa: E402
from app.services.pdf_processor import PDFProcessingError, process_pdf  # noqa: E402
from app.services.vector_store import delete_document_chunks, index_chunks  # noqa: E402

UPLOAD_DIR = BASE_DIR / settings.upload_dir


def main():
    db = SessionLocal()
    try:
        documents = db.scalars(select(Document).order_by(Document.id)).all()
        print(f"Found {len(documents)} document(s).")

        for doc in documents:
            path = UPLOAD_DIR / doc.stored_filename
            if not path.exists():
                print(f"  SKIP  [{doc.id}] {doc.title}: file missing on disk")
                continue
            try:
                _, chunks = process_pdf(path)
            except PDFProcessingError as exc:
                print(f"  FAIL  [{doc.id}] {doc.title}: {exc}")
                continue

            delete_document_chunks(doc.id)  # avoids duplicates on re-runs
            index_chunks(doc.id, doc.title, doc.access_level, chunks)
            doc.chunk_count = len(chunks)
            print(f"  OK    [{doc.id}] {doc.title}: {len(chunks)} chunks indexed")

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()