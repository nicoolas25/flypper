from abc import ABC, abstractmethod
from typing import List

from flypper.entities.flag import Flag, UnversionedFlagData

class AbstractStorage(ABC):
    @abstractmethod
    def list(self, version__gt: int = 0) -> List[Flag]:
        return []

    @abstractmethod
    def upsert(self, flag: UnversionedFlagData) -> Flag:
        return None
