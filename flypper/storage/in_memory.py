from time import time
from typing import Dict, List, cast

from flypper.entities.flag import Flag, FlagData, UnversionedFlagData
from flypper.storage.abstract import AbstractStorage

class InMemoryStorage(AbstractStorage):
    def __init__(self):
        self._version: int = 0
        self._flags: Dict[str, Flag] = {}

    def list(self, version__gt: int = 0) -> List[Flag]:
        return [
            flag
            for flag in self._flags.values()
            if flag.version > version__gt
        ]

    def upsert(self, flag_data: UnversionedFlagData) -> Flag:
        self._version = self._version + 1
        name = flag_data["name"]
        flag = Flag(
            data=cast(FlagData, {
                **flag_data,
                "updated_at": time(),
                "version": self._version,
            }),
        )
        self._flags[name] = flag
        return flag

    def delete(self, flag_name: str) -> None:
        del self._flags[flag_name]
