from typing import Literal

from pydantic import BaseModel


class ReviewScores(BaseModel):
    accuracy: int
    completeness: int
    groundedness: int
    professionalism: int


class ReviewResult(BaseModel):
    status: Literal["PASS", "FAIL"]
    scores: ReviewScores
    feedback: list[str]