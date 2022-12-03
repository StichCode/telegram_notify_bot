import json
import os
from pathlib import Path

import pytest

from src.dto.user import User


@pytest.fixture
def users() -> list[User]:
    with open(Path(os.path.dirname(__file__), 'fixtures', 'users.json'), 'r') as file:
        return [User(**d) for d in json.load(file)]
