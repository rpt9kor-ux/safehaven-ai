import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.pdf_processor import Chunk  # noqa: E402
from app.services.vector_store import (  # noqa: E402
    delete_document_chunks,
    index_chunks,
    search,
)

TEST_DOC_ID = 999999

general = [
    Chunk("Employees receive 8 weeks of paid parental leave after the birth or adoption of a child.", 12),
    Chunk("All staff must wear safety helmets and steel-toe boots inside the warehouse.", 4),
    Chunk("Vacation requests must be submitted at least two weeks in advance.", 7),
]
secret = [
    Chunk("Executive severance packages are equal to 12 months of base salary.", 3),
]

print("Indexing test chunks (the first run downloads the model)...")
index_chunks(TEST_DOC_ID, "Test General Policy", "general", general)
index_chunks(TEST_DOC_ID + 1, "Test HR Confidential", "hr_only", secret)

question = "How much time off do new parents get?"

print(f"\nQuestion: {question}")
print("\n--- As an EMPLOYEE (general only) ---")
for hit in search(question, ["general"], limit=2):
    print(f"{hit['score']:.2f} | {hit['title']}, Page {hit['page_number']} | {hit['text'][:70]}")

print("\n--- Employee asks about salary (must NOT return the HR-only chunk) ---")
for hit in search("What is the executive severance?", ["general"], limit=2):
    print(f"{hit['score']:.2f} | {hit['title']} | {hit['text'][:70]}")

print("\n--- As HR ADMIN (all levels) ---")
for hit in search("What is the executive severance?", ["general", "hr_only"], limit=1):
    print(f"{hit['score']:.2f} | {hit['title']} | {hit['text'][:70]}")

# Clean up the test data
delete_document_chunks(TEST_DOC_ID)
delete_document_chunks(TEST_DOC_ID + 1)
print("\nTest data removed.")