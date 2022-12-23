import json
import os
from pathlib import Path

import pytest
import pytest_asyncio

from src.dto.user import User

from time import sleep

import pytest
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.custom import Conversation


@pytest_asyncio.fixture
def users() -> list[User]:
    with open(Path(os.path.dirname(__file__), 'fixtures', 'users.json'), 'r') as file:
        return [User(**d) for d in json.load(file)]




@pytest_asyncio.fixture(scope="session")
async def telegram_client():
    with TelegramClient(
        StringSession(session), api_id, api_hash, sequential_updates=True
    ) as client:
        await client.connect()
        await client.get_me()
        await client.get_dialogs()

        yield client

        await client.disconnect()
        await client.disconnected


@pytest.fixture(scope="session")
async def conv(telegram_client):
    """Open conversation with the bot."""
    async with telegram_client.conversation(
        'tests_100_bot', timeout=10, max_messages=10000
    ) as conv:
        conv: Conversation

        # These are bot-specific preparation steps. In listOK /start
        # command registers the user and sends a welcome message and
        # a list of user's lists with the main menu. These messages
        # must be awaited before yielding control to tests.
        msg = await conv.send_message("/start")
        res1 = await conv.get_response()  # Welcome message
        res = await conv.get_response()  # User lists
        sleep(10)
        yield conv
