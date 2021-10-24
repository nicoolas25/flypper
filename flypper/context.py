from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from flypper.client import Client
    from flypper.entities.flag import Flag

class Context:
    """Context allows to retrieve flags consistently across its lifetime.

    The context won't call the client more than once. When it does, it will
    retrieve all flags from its client and keep using those as reference.

    It also stores a list of context's entries to use when checking flags,
    so we don't have to pass them everywhere.
    """

    def __init__(self, client: "Client", entries: Dict[str, str] = {}):
        self._client: "Client" = client
        self._common_entries: Dict[str, str] = entries.copy()
        self._synced: bool = False
        self._flags_cache: Dict[str, "Flag"] = {}

    def is_enabled(self, flag_name: str, **entries: str) -> bool:
        """Checks if a flag is enabled given the context's entries.

        Also takes a list of entries to override the context's ones."""
        flag = self._flags().get(flag_name, None)
        return bool(flag and flag.is_enabled(**self._common_entries, **entries))

    def is_disabled(self, flag_name: str, **entries: str) -> bool:
        """Does the opposite of is_enabled: checks if a flag is disabled, given the context's entries."""
        return not self.is_enabled(flag_name=flag_name, **entries)

    #
    # Use [] to get and set the context's entries
    #

    def __getitem__(self, entry_name) -> Optional[str]:
        return self._common_entries.get(entry_name, None)

    def __setitem__(self, entry_name, entry_value) -> None:
        self._common_entries[entry_name] = entry_value

    #
    # Use the context as a context manager
    #

    def __enter__(self) -> "Context":
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        pass

    def _flags(self) -> Dict[str, "Flag"]:
        """Retrieves all flags from the client once then keep returning them."""
        if not self._synced:
            self._flags_cache = self._client.flags()
            self._synced = True
        return self._flags_cache
