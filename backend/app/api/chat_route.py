from fastapi import APIRouter, Request

from ..schemas.chat_schema import (
    ChatRequest,
    ChatResponse,
)

router = APIRouter(tags=["Chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(request: Request, payload: ChatRequest):

    graph = request.app.state.graph

    result = graph.invoke(
        {
            "question": payload.question,
            "customer_id": payload.customer_id,
            "thread_id": payload.thread_id,
            "messages": [],
            "route": "",
            "documents": [],
            "answer": "",
            "review": "",
            "confidence": 0.0,
            "feedback": [],
            "priority": "normal",
            "assigned_team": "",
            "sources": [],
            "memory_updates": [],
            "final_answer": "",
            "retry_count": 0,
        }
    )

    print(result["confidence"])

    return ChatResponse(
        question=payload.question,
        route=result["route"],
        answer=result["answer"],
        review=result.get("review", ""),
        confidence=result.get("confidence", 0.0),
        priority=result.get("priority", "normal"),
        assigned_team=result.get("assigned_team", ""),
        sources=result.get("sources", []),
        feedback=result.get("feedback", []),
        review_scores=result.get("review_scores"),
        ticket_id=result.get("ticket_id"),
        #memory_updates=result.get("memory_updates", []),
        final_answer=result.get("final_answer", result["answer"]),
    )