import random

from loguru import logger


class MeowCache:
    def __init__(self) -> None:
        self.data: list[bytes] = []

    def add(self, meows: list[bytes]) -> None:
        self.data.extend(meows)

    def get(self) -> bytes:
        return random.choice(self.data)
