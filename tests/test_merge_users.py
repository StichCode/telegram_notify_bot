from src.bot.admin.utils import merge_users
from src.dto.user import User


def test_merge_users(users: list[User]) -> None:
    excel_users = [
        User(tg_id=1, name='rubert', phone='89664284491'),
        User(tg_id=1, name='alex'),
        User(tg_id=1, phone='89668302555'),
        User(tg_id=1, name='rabbit', phone='89771111111'),
        User(tg_id=1, name='от кого-то')
    ]
    merged = merge_users(db_users=users, excel_users=excel_users)
    assert len(merged) == 3
