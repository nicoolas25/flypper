from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from flypper.client import Client
    from flypper.entities.flag import Flag

class Context:
    def __init__(self, client: "Client", entries: Dict[str, str] = {}):
        self._client: "Client" = client
        self._common_entries: Dict[str, str] = entries.copy()
        self._synced: bool = False
        self._flags: Dict[str, "Flag"] = {}

    def flags(self) -> Dict[str, "Flag"]:
        if not self._synced:
            self._flags = dict(self._client.flags())
            self._synced = True
        return self._flags

    def is_enabled(self, flag_name: str, **entries: str) -> bool:
        flag = self.flags().get(flag_name, None)
        return bool(flag and flag.is_enabled(**self._common_entries, **entries))

    def is_disabled(self, flag_name: str, **entries: str) -> bool:
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
