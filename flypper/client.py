from time import monotonic
from threading import Semaphore
from typing import Callable, Dict, TYPE_CHECKING

from flypper.context import Context

if TYPE_CHECKING:
    from flypper.entities.flag import Flag
    from flypper.storage.abstract import AbstractStorage

class Client:
    """Client caches the flags' configuration at the application level.

    A client set a TTL: the maximum duration it can serve flags without synchronizing
    with the storage backend.

    It efficiently synchronize by only asking for the updates since its last sync.
    To get there, the storage and the client agree on a global version number associated
    with each update.
    """

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
        self._semaphore: Semaphore = Semaphore()

    def flags(self) -> Dict[str, "Flag"]:
        """Lists the flag, by their name.

        It will call the storage at most once every ttl seconds, fetching
        only the latest updates since the last storage roundtrip.
        """
        self._sync()
        return self._flags

    def __call__(self, **entries: str) -> Context:
        """Builds a context from this client."""
        return Context(client=self, entries=entries)

    def _sync(self):
        """Syncs the cache with the storage."""
        with self._semaphore:
            now = self._time_fn()

            if now < self._next_sync:
                return

            # Get the latest flags updates from the backend.
            new_flags = self._storage.list(version__gt=self._last_version)

            if new_flags:
                # Don't directly update the _flags, create a copy so the running contexts
                # can operate using the reference of the outdated copy they might have.
                self._flags = self._flags.copy()

                # Update the cached flags with their latest version.
                for new_flag in new_flags:
                    if new_flag.is_deleted:
                        del self._flags[new_flag.name]
                    else:
                        self._flags[new_flag.name] = new_flag

                # Keep track of the latest version we received.
                self._last_version = max(flag.version for flag in new_flags)

            # Compute the minimum time the next sync could occur.
            self._next_sync = now + self._ttl
