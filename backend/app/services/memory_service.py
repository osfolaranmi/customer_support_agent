from collections import defaultdict

class MemoryService:
    def __init__(self):
        self._memory = defaultdict(list)

    def get_history(self, thread_id: str):
        return self._memory[thread_id]

    def add_user_message(self, thread_id: str, message: str):
        self._memory[thread_id].append({
            "role": "user",
            "content": message
        })

    def add_assistant_message(self, thread_id: str, message: str):
        self._memory[thread_id].append({
            "role": "assistant",
            "content": message
        })

memory_service = MemoryService()