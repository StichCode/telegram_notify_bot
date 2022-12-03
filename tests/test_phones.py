import pytest

from src.dto.user import User

EXAMPLES = [
    ("+79776508536", '79776508536'),
    ("79776508536", '79776508536'),
    ("7 977 650 85 36", '79776508536'),
    ("+7 (977) 650 85 36", '79776508536'),
    ("+7(977) 650 85 36", '79776508536'),
    ("+7(977)650 85 36", '79776508536'),
    ("+7(977) 6508536", '79776508536'),
    ("+7(977)650 8536", '79776508536'),
    ("+7(977)65085 36", '79776508536'),
    ("+7(97 7)65 085 3 6", '79776508536'),
    ("+7(977)6508536", '79776508536'),
    ("+7(977)650-85-36", '79776508536'),
    ("7(977)6508536", '79776508536'),
    ("+7(977)650-85-36", '79776508536'),
    ("89776508536", '79776508536'),
    ("8(977)6508536", '79776508536'),
    ("8 977 650 85 36", '79776508536'),
    ("+79776508536", '79776508536')
]


@pytest.mark.parametrize("phone,expected", EXAMPLES)
def test_phone_validator(phone: str, expected: int):
    u = User(
        tg_id=0,
        phone=phone
    )
    assert u.phone == expected
