from fastapi import FastAPI
from pydantic import BaseModel

from app.ai.graph import run_graph_with_metadata


app = FastAPI(
    title="Insurance AI API",
    description=(
        "API for the Insurance AI assistant powered "
        "by LangGraph, Azure SQL and RAG."
    ),
    version="1.0.0",
)


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    tools_used: list[str]
    request_id: str


@app.get("/health")
def health_check():
    """
    Basic health endpoint for deployment monitoring.
    """
    return {
        "status": "healthy",
    }


@app.post(
    "/ask",
    response_model=AskResponse,
)
def ask_question(
    request: AskRequest,
):
    """
    Send a question through the Insurance AI
    LangGraph workflow.
    """

    result = run_graph_with_metadata(
        request.question
    )

    return AskResponse(
        answer=result["answer"],
        tools_used=result["tools_used"],
        request_id=result["request_id"],
    )