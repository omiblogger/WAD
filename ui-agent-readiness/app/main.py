"""Day 1: run via `python -m uvicorn app.main:app --reload`. Open /docs."""
import os
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from app.logic import calculate_emi
from app.retrieval import retrieve
from app.llm import answer_with_azure
from fastapi.testclient import TestClient

load_dotenv()
app = FastAPI(title="Banking AI Assistant - EY Readiness Lab", version="0.1.2")


class Question(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class EMIRequest(BaseModel):
    principal: float = Field(gt=0)
    annual_rate: float = Field(ge=0)
    years: int = Field(gt=0, le=50)

Client = TestClient(app)

def test_health_endpoint():
    response = Client.get("/health")
    assert response.status_code ==200
    assert response.json() =={
        "status": "ok",
        "service": "banking-ai-assistant",
        "version": app.version
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "banking-ai-assistant", "version": app.version}


@app.post("/search")
def search(request: Question):
    """Local word-overlap retrieval; NOT vector search yet."""
    return {"retrieval_mode": "local-keyword-baseline", "documents": retrieve(request.question)}


@app.post("/emi")
def emi(request: EMIRequest):
    return {"monthly_emi": calculate_emi(request.principal, request.annual_rate, request.years), "currency": "INR"}


@app.post("/chat")
def chat(request: Question, x_app_token: str | None = Header(default=None)):
    """Authenticated demo route. Don't expose publicly without real production auth."""
    expected_token = os.getenv("APP_ACCESS_TOKEN")
    if not expected_token or x_app_token != expected_token:
        raise HTTPException(status_code=401, detail="Set APP_ACCESS_TOKEN and send X-App-Token header")
    docs = retrieve(request.question)
    try:
        answer = answer_with_azure(request.question, docs)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"answer": answer, "sources": [doc["id"] for doc in docs]}
