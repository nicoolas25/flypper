from flypper.entities.flag import UnversionedFlagData

def create_flag_data(name) -> UnversionedFlagData:
    return {
        "name": name,
        "enabled": True,
        "deleted": False,
        "enabled_for_actors": None,
        "enabled_for_percentage_of_actors": None,
    }
