import os
import json
from typing import Any

cache: dict[Any, Any] = {}

config_file_name = "config.json"
config_example_file_name = "config.example.json"


def getenv(_key: str, environment_variable_mode: bool = True) -> Any:
    """**Get value of environment variable**
    Args:
        _key (str): The name of the environment variable
        environment_variable_mode (bool): Select the environment variable mode, default is True
    Return:
        Any: The value of the environment variable
    """
    if _key.islower():
        key = _key.upper()
    else:
        key = _key

    if key in cache:
        return cache[key]

    if not environment_variable_mode:
        if not os.path.exists(config_file_name):
            with open(config_example_file_name, "r", encoding="utf-8") as fp:
                copy = fp.read()
                fp.close()

                config_fp = open(config_file_name, "w+")
                config_fp.write(copy)
                config_fp.flush()
                config_fp.close()

        with open(config_file_name, "r", encoding="utf-8") as fp:
            data = json.loads(fp.read())
            cache[key] = data.get(key)
    else:
        cache[key] = os.environ.get(key)
    return cache[key]


def overrideenv(key: str, value: str):
    cache[key] = value