import pytest
from telethon.tl.custom import Conversation


# async def get_user_lists(conv: Conversation):
#     """Return message with user's lists and main menu."""
#     await conv.send_message("/help")
#     sleep(10)
#     return await conv.get_response()


@pytest.mark.asyncio
async def test_fucking(conv: Conversation):
    """Test /my_lists bot command."""
    await conv.send_message("/start")
    user_lists = await conv.get_response()

    # Check that the message contains necessary text
    assert "Choose list or action" in user_lists.text
    # Check that there is a button inviting a user to create a list
    # assert get_button_with_text(user_lists, "Create new list") is not None
