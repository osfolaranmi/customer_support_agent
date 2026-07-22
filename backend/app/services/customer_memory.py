from collections import defaultdict

class CustomerMemory:

    def __init__(self):
        self._memory = defaultdict(dict)

    def get(self, customer_id: str):
        return self._memory[customer_id]

    def update(self, customer_id: str, updates: dict):
        self._memory[customer_id].update(updates)

customer_memory = CustomerMemory()