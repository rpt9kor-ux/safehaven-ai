from fastapi import FastAPI

app = FastAPI(
    title="SafeHaven HR & Compliance AI",
    description="RAG-based assistant for HR policy questions with citations.",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"message": "Welcome to SafeHaven AI"}


@app.get("/health")
def health_check():
    return {"status": "ok"}