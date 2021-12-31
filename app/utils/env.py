import os
import ujson

cache = {}

config_file_name = "config.json"
config_example_file_name = "config.example.json"


def getenv(key: str):
    if key in cache:
        return cache[key]

    if not os.path.exists(config_file_name):
        with open(config_example_file_name, "r", encoding="utf-8") as fp:
            copy = fp.read()
            fp.close()

            config_fp = open(config_file_name, "w+")
            config_fp.write(copy)
            config_fp.flush()
            config_fp.close()

    with open(config_file_name, "r", encoding="utf-8") as fp:
        data = ujson.loads(fp.read())
        cache[key] = data.get(key)

    return cache[key]


def overrideenv(key: str, value: str):
    cache[key] = value