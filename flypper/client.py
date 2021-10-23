from time import monotonic
from typing import Callable, Dict, TYPE_CHECKING

from flypper.context import Context

if TYPE_CHECKING:
    from flypper.entities.flag import Flag
    from flypper.storage.abstract import AbstractStorage

class Client:
    def __init__(
        self,
        storage: "AbstractStorage",
        ttl: float = 5.0,
        time_fn: Callable[[], float] = monotonic,
    ):
        self._storage: "AbstractStorage" = storage
        self._ttl: float = ttl
        self._last_version: int = 0
        self._next_sync: float = 0
        self._flags: Dict[str, "Flag"] = {}
        self._time_fn: Callable[[], float] = time_fn

    def flags(self) -> Dict[str, "Flag"]:
        self._sync()
        return self._flags

    def __call__(self, **entries: str) -> Context:
        return Context(client=self, entries=entries)

    def _sync(self):
        now = self._time_fn()

        if now < self._next_sync:
            return

        # Get the latest flags from the backend
        new_flags = self._storage.list(version__gt=self._last_version)

        if new_flags:
            # Update cache
            for new_flag in new_flags:
                if new_flag.is_deleted:
                    del self._flags[new_flag.name]
                else:
                    self._flags[new_flag.name] = new_flag
            self._last_version = max(flag.version for flag in new_flags)

        self._next_sync = now + self._ttl
