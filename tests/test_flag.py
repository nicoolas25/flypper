from typing import cast

from flypper import Flag, FlagData

def test_deleted_flag():
    flag = create_flag(deleted=True)
    assert not flag.is_enabled()

def test_disabled_flag():
    flag = create_flag(enabled=False)
    assert not flag.is_enabled()

def test_enabled_flag():
    flag = create_flag(enabled=True)
    assert flag.is_enabled()

def test_enabled_for_actors_flag():
    flag = create_flag(enabled_for_actors={
        "actor_key": "user_id",
        "actor_ids": ["8", "6"],
    })
    assert flag.is_enabled(user_id="6")
    assert not flag.is_enabled(user_id="5")
    assert not flag.is_enabled()

def test_enabled_for_percentage_of_actors_flag():
    flag = create_flag(enabled_for_percentage_of_actors={
        "actor_key": "user_id",
        "percentage": 55.55,
    })
    assert flag.is_enabled(user_id="7")
    assert not flag.is_enabled(user_id="53")
    assert not flag.is_enabled()


def create_flag(**overrides):
    return Flag(
        data=cast(FlagData, {
            "name": "test",
            "enabled": True,
            "deleted": False,
            "enabled_for_actors": None,
            "enabled_for_percentage_of_actors": None,
            "updated_at": 0.0,
            "version": 0,
            **overrides,
        }),
    )
