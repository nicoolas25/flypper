from abc import ABC, abstractmethod
from typing import List

from flypper.entities.flag import Flag, UnversionedFlagData

class AbstractStorage(ABC):
    @abstractmethod
    def list(self, version__gt: int = 0) -> List[Flag]:
        """Lists all flags that has been 'upserted' after the given version number."""
        raise NotImplementedError

    @abstractmethod
    def upsert(self, flag_data: UnversionedFlagData) -> Flag:
        """Inserts a flag, setting a 'version' and a 'updated_at' from an UnversionedFlagData."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, flag_name: str) -> None:
        """Fully remove a flag from the store.

        Note that soft-delete occurs by upserting a flag with a 'deleted=True' mapping."""
        raise NotImplementedError
