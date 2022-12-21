from loguru import logger

import pandas as pd
import requests

from src.dto.user import User
from src.dto.user_data import UserData
from src.errors import BadPhoneNumber, BadColumnName

DictUser = dict[str, str]


def get_xlsx(file_url: str) -> pd.DataFrame:
    resp = requests.get(file_url, verify=False)
    df = pd.read_excel(resp.content)
    # pre-prettify df columns
    df.rename(columns={c: c.strip().lower() for c in df.columns}, inplace=True)
    return df


def get_file(ud: UserData) -> tuple[list[User], list[DictUser]] | None:
    df = get_xlsx(ud.file_path)
    users = []
    bad_data = []
    logger.info(ud)
    if ud.column_phone not in df.columns:
        raise BadColumnName(ud.column_phone)
    df[ud.column_phone] = df[ud.column_phone].fillna('')
    # fixme: dirty hack
    cols = [i.replace('.0', '').strip() for i in df[ud.column_phone].dropna().astype(str).tolist()]
    for phone in cols:
        try:
            users.append(User(tg_id=1, phone=phone))
        except (ValueError, BadPhoneNumber) as ex:
            bad_data.append(phone)
            logger.error("Bad data for parsing: {}".format(phone))
            logger.error(ex)
            continue
    return users, bad_data


def merge_users(db_users: list[User], excel_users: list[User]) -> list[User]:
    merged = []
    for dbu in db_users:
        for exu in excel_users:
            eq_phone = exu.phone and dbu.phone and dbu.phone == exu.phone
            eq_name = dbu.name and exu.name and dbu.name == exu.name
            if (eq_phone or eq_name) and exu not in merged:
                exu.name = dbu.name
                exu.phone = dbu.phone
                exu.tg_id = dbu.tg_id
                merged.append(exu)
    logger.info('Merged {}, input users: {}'.format(len(merged), len(excel_users)))
    return merged


def to_sublist(d: list, *, sep: int = 4) -> list[list]:
    return [d[x:x + sep] for x in range(0, len(d), sep)]
