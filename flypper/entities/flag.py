from hashlib import md5
from typing import Dict, List, Optional
from typing_extensions import TypedDict

class _EnabledForActors(TypedDict):
    actor_key: str
    actor_ids: List[str]

class _EnabledForPercentageOfActors(TypedDict):
    actor_key: str
    percentage: float

class UnversionedFlagData(TypedDict):
    name: str
    deleted: bool
    enabled: bool
    enabled_for_actors: Optional[_EnabledForActors]
    enabled_for_percentage_of_actors: Optional[_EnabledForPercentageOfActors]

class FlagData(UnversionedFlagData):
    updated_at: float
    version: int

class Flag:
    def __init__(self, data: FlagData):
        self.data: FlagData = data.copy()
        self.name: str = self.data["name"]
        self.is_deleted: bool = self.data["deleted"]
        self.version: int = self.data["version"]

    def is_enabled(self, **entries: str) -> bool:
        return (
            self.is_deleted is False
            and self.data["enabled"]
            and self._is_enabled_for_actors(entries)
            and self._is_enabled_for_percentage_of_actors(entries)
        )

    def _is_enabled_for_actors(self, entries: Dict[str, str]) -> bool:
        enabled_for_actors = self.data["enabled_for_actors"]

        if enabled_for_actors is None:
            return True

        actor_id = entries.get(enabled_for_actors["actor_key"], None)

        if actor_id is None:
            return False

        return actor_id in enabled_for_actors["actor_ids"]

    def _is_enabled_for_percentage_of_actors(self, entries: Dict[str, str]) -> bool:
        enabled_for_percentage_of_actors = self.data["enabled_for_percentage_of_actors"]

        if enabled_for_percentage_of_actors is None:
            return True

        flag_percentage = enabled_for_percentage_of_actors["percentage"]

        if flag_percentage == 100.00:
            return True

        actor_id = entries.get(enabled_for_percentage_of_actors["actor_key"], None)

        if actor_id is None:
            return False

        actor_md5 = md5(actor_id.encode("utf-8")).digest()
        actor_percentage = (int.from_bytes(actor_md5, "big") % 100_00) / 100.00

        return actor_percentage <= flag_percentage
