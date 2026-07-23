import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


class HandoffQueue:

    def __init__(self):
        self.file = Path("app/data/handoff_queue.json")
        self.file.parent.mkdir(parents=True, exist_ok=True)

        if not self.file.exists():
            self.file.write_text("[]")

    def enqueue(
        self,
        customer_id: str,
        question: str,
        priority: str,
        assigned_team: str,
        route: str,
    ):

        with self.file.open("r") as f:
            queue = json.load(f)

        ticket = {
            "ticket_id": f"HND-{uuid4().hex[:8].upper()}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "customer_id": customer_id,
            "question": question,
            "route": route,
            "priority": priority,
            "assigned_team": assigned_team,
            "status": "Pending"
        }

        queue.append(ticket)

        with self.file.open("w") as f:
            json.dump(queue, f, indent=4)

        return ticket