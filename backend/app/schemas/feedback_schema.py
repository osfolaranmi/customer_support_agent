from typing import Literal

from pydantic import BaseModel


class FeedbackRequest(BaseModel):
    customer_id: str
    thread_id: str
    question: str
    answer: str
    rating: Literal[
        "helpful",
        "not_helpful",
    ]


class FeedbackResponse(BaseModel):
    message: str