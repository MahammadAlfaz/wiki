import time


from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.query_log import QueryLog
from app.models.user import User
from app.graph.rag_graph import rag_workflow


router = APIRouter(prefix="/query", tags=["query"])


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    web_search_used: bool
    hallucination_score: float


@router.post("/chat", response_model=QueryResponse)
def chat(
    req: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty ")

    start = time.time()

    initial_state = {
        "question": req.question,
        "user_id": str(current_user.id),
        "user_role": current_user.role,
        "transformed_query": "",
        "should_retrieve": True,
        "retrieved_docs": [],
        "graded_docs": [],
        "web_search_used": False,
        "generated_answer": "",
        "hallucination_score": 0.0,
        "attempts": 0,
        "final_answer": "",
        "sources": [],
    }
    result = rag_workflow.invoke(initial_state)
    elapsed = round(time.time() - start, 2)

    log = QueryLog(
        user_id=current_user.id,
        question=req.question,
        final_answer=result.get("final_answer", ""),
        sources=result.get("sources", []),
        hallucination_score=result.get("hallucination_score", 0.0),
        web_search_used=result.get("web_search_used", False),
        response_time=elapsed,
    )
    db.add(log)
    db.commit()

    return QueryResponse(
        answer=result.get("final_answer", "No answer generated"),
        sources=result.get("sources", []),
        web_search_used=result.get("web_search_used", False),
        hallucination_score=result.get("hallucination_score", 0.0),
    )


@router.get("/history")
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 20,
):
    logs = (
        db.query(QueryLog)
        .filter(QueryLog.user_id == current_user.id)
        .order_by(QueryLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": log.id,
            "question": log.question,
            "answer": log.final_answer,
            "sources": log.sources,
            "web_search_used": log.web_search_used,
            "hallucination_score": log.hallucination_score,
            "response_time": log.response_time,
            "created_at": log.created_at,
        }
        for log in logs
    ]
