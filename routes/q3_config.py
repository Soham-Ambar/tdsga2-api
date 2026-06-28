from fastapi import APIRouter, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

router = APIRouter()

DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

YAML_CONFIG = {
    "debug": False,
    "api_key": "key-0a1tyft9d3",
}

DOTENV_CONFIG = {
    "APP_LOG_LEVEL": "info",
}

OS_ENV_CONFIG = {
    "APP_LOG_LEVEL": "debug",
    "APP_API_KEY": "key-hd0184ubu8",
}


def normalize_key(key: str) -> str:
    key = key.strip()

    if key.startswith("APP_"):
        key = key[4:]

    if key == "NUM_WORKERS":
        return "workers"

    return key.lower()


def coerce_value(key: str, value):
    if key in ["port", "workers"]:
        return int(value)

    if key == "debug":
        if isinstance(value, bool):
            return value
        return str(value).lower() in ["true", "1", "yes", "on"]

    return str(value)


def merge_env_layer(config: dict, env_layer: dict):
    for raw_key, value in env_layer.items():
        key = normalize_key(raw_key)
        config[key] = value


def finalize_config(config: dict):
    result = {}

    for key, value in config.items():
        result[key] = coerce_value(key, value)

    result["api_key"] = "****"

    return {
        "port": result.get("port"),
        "workers": result.get("workers"),
        "debug": result.get("debug"),
        "log_level": result.get("log_level"),
        "api_key": result.get("api_key"),
    }


@router.get("/effective-config")
def effective_config(set: Optional[List[str]] = Query(default=None)):
    config = {}

    # 1. defaults
    config.update(DEFAULTS)

    # 2. config.development.yaml
    config.update(YAML_CONFIG)

    # 3. .env
    merge_env_layer(config, DOTENV_CONFIG)

    # 4. OS env variables
    merge_env_layer(config, OS_ENV_CONFIG)

    # 5. CLI overrides from query params
    if set:
        for item in set:
            if "=" in item:
                key, value = item.split("=", 1)
                key = normalize_key(key)
                config[key] = value

    return finalize_config(config)