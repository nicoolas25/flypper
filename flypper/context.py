from typing import Dict

from flypper.client import Client
from flypper.entities.flag import Flag

class Context:
    def __init__(self, client: Client, entries: Dict[str, str] = {}):
        self._client: Client = client
        self._common_entries: Dict[str, str] = entries
        self._synced: bool = False
        self._flags: Dict[str, Flag] = {}

    def flags(self) -> Dict[str, Flag]:
        if not self._synced:
            self._flags = dict(self._client.flags())
            self._synced = True
        return self._flags

    def is_enabled(self, flag_name: str, entries: Dict[str, str] = {}) -> bool:
        flag = self.flags().get(flag_name, None)
        return bool(flag and flag.is_enabled({**self._common_entries, **entries}))
