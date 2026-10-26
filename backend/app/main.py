from fastapi import FastAPI

from app.api import health

app = FastAPI(
    title="SafeHaven HR & Compliance AI",
    description="RAG-based assistant for HR policy questions with citations.",
    version="0.1.0",
)

app.include_router(health.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to SafeHaven AI"}