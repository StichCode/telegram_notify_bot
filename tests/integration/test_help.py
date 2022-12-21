import pytest

from src.bot import help_handler

token = '5626885931:AAFTvtex-9xQulPnyaKaKPZYlC0FAHEmdhI'

@pytest.fixture()
def mock_sum(mocker):
    future = asyncio.Future()
    future.set_result(4)
    mocker.patch('app.sum', return_value=future)


@pytest.mark.asyncio
async def test_sum(mock_sum):
    result = await sum(1, 2)
    # I know 1+2 is equal to 3 but one man can only dream!
    assert result == 4


@pytest.mark.asyncio
def test_help_admin():
    await help_handler()
