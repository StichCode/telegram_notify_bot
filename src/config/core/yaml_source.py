import os.path
from pathlib import Path
from typing import Any

import yaml
from pydantic.env_settings import BaseSettings


def yaml_settings(settings: BaseSettings) -> dict[str, Any]:
    encoding = settings.__config__.env_file_encoding
    p = Path(os.path.dirname(__file__), '../messages.yaml')
    with open(p, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)
