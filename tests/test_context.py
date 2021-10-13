from typing import cast

from flypper.client import Client
from flypper.context import Context
from flypper.entities.flag import UnversionedFlagData

from tests.factories import create_flag_data
from tests.fake_storage import FakeStorage

def test_context_retrieves_at_most_once_from_client():
    storage = FakeStorage()
    client = Client(storage=storage, ttl=0)
    context = Context(client=client, entries={})

    context.flags()
    context.flags()
    assert storage.list_call_count == 1

def test_context_saves_a_local_copy_of_the_flags():
    storage = FakeStorage()
    client = Client(storage=storage, ttl=0)
    context = Context(client=client, entries={})
    flag_data = create_flag_data(name="foo")

    storage.upsert(flag_data)
    assert client.flags()["foo"].is_enabled(entries={})
    assert context.is_enabled(flag_name="foo", entries={})

    storage.upsert(cast(UnversionedFlagData, {**flag_data, "enabled": False}))
    assert not client.flags()["foo"].is_enabled(entries={})
    assert context.is_enabled(flag_name="foo", entries={})
