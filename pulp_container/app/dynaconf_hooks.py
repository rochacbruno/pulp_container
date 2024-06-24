
from typing import Any
from dynaconf import Dynaconf, Validator


def post(settings: Dynaconf) -> dict[str, Any]:

    # Add a new validator to Dynaconf
    settings.validators.register(
        Validator("POTATO", must_exist=True),
        Validator("plugin.name", startswith="pulp"),
    )
    settings.validators.validate_all()

    return {}
