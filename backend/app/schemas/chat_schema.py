from typing import List, Literal, Optional

from pydantic import BaseModel


class Source(BaseModel):
    source: str
    content_preview: str


class ChatRequest(BaseModel):
    customer_id: str
    thread_id: str
    question: str

class ReviewScores(BaseModel):
    accuracy: int
    completeness: int
    groundedness: int
    professionalism: int

    
class ChatResponse(BaseModel):
    question: str

    route: Literal[
        "knowledge",
        "troubleshooting",
        "escalation",
        "onboarding",
        "general"
    ]

    answer: str

    review: str

    confidence: float

    review_scores: ReviewScores | None = None


    priority: Literal[
        "low",
        "normal",
        "urgent"
    ]

    assigned_team: str
    feedback: list[str] = []
    sources: List[Source]

    #memory_updates: List[str]

    final_answer: str
    ticket_id:  Optional[str] = None
