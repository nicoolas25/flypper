from typing import cast

from flypper.client import Client
from flypper.entities.flag import UnversionedFlagData

from tests.factories import create_flag_data
from tests.fake_storage import FakeStorage

def test_client_fetches_flags_from_storage():
    storage = FakeStorage()
    client = Client(storage=storage, ttl=0)

    client.flags()
    client.flags()

    assert storage.list_call_count == 2

def test_client_uses_a_cache_valid_for_ttl_seconds():
    storage = FakeStorage()
    client = Client(storage=storage, ttl=1)

    client.flags()
    client.flags() # TTL isn't crossed

    assert storage.list_call_count == 1

def test_client_cleans_deleted_flags_during_sync():
    storage = FakeStorage()
    client = Client(storage=storage, ttl=0)
    flag_data = create_flag_data(name="foo")

    storage.upsert(flag_data)
    assert "foo" in client.flags()

    storage.upsert(cast(UnversionedFlagData, {**flag_data, "deleted": True}))
    assert "foo" not in client.flags()

def test_client_refresh_updated_flags_during_sync():
    storage = FakeStorage()
    client = Client(storage=storage, ttl=0)
    flag_data = create_flag_data(name="foo")

    storage.upsert(flag_data)
    assert client.flags()["foo"].is_enabled(entries={})

    storage.upsert(cast(UnversionedFlagData, {**flag_data, "enabled": False}))
    assert not client.flags()["foo"].is_enabled(entries={})
