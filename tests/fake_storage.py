from typing import List

from flypper.entities.flag import Flag
from flypper.storage.in_memory import InMemoryStorage

class FakeStorage(InMemoryStorage):
    def __init__(self):
        super().__init__()
        self.list_call_count = 0

    def list(self, *args, **kwargs) -> List[Flag]:
        self.list_call_count = self.list_call_count + 1
        return super().list(*args, **kwargs)
