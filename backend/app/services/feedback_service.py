import json
import uuid
from datetime import datetime
from pathlib import Path


class FeedbackService:

    def __init__(self):

        self.file_path = (
            Path(__file__).parent.parent
            / "data"
            / "feedback.json"
        )

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.file_path.exists():
            self.file_path.write_text("[]")

    def save(
        self,
        customer_id: str,
        thread_id: str,
        question: str,
        answer: str,
        rating: str,
    ):

        with open(self.file_path, "r") as file:
            feedback = json.load(file)

        record = {
            "id": str(uuid.uuid4()),
            "customer_id": customer_id,
            "thread_id": thread_id,
            "question": question,
            "answer": answer,
            "rating": rating,
            "created_at": datetime.utcnow().isoformat(),
        }

        feedback.append(record)

        with open(self.file_path, "w") as file:
            json.dump(
                feedback,
                file,
                indent=4,
            )

        return record


feedback_service = FeedbackService()