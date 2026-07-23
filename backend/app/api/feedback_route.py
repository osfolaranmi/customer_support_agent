from fastapi import APIRouter

from ..schemas.feedback_schema import (
    FeedbackRequest,
    FeedbackResponse,
)

from ..services.feedback_service import (
    feedback_service,
)

router = APIRouter(tags=["Feedback"])


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
)
def submit_feedback(payload: FeedbackRequest):

    feedback_service.save(
        customer_id=payload.customer_id,
        thread_id=payload.thread_id,
        question=payload.question,
        answer=payload.answer,
        rating=payload.rating,
    )

    return FeedbackResponse(
        message="Feedback received. Thank you!"
    )