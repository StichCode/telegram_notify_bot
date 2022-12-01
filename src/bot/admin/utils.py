from loguru import logger

import pandas as pd
import requests

from src.dto.user import User


def get_file(file_url: str, col_name: str, col_phone: str) -> list[User] | None:
    resp = requests.get(file_url, verify=False)
    df = pd.read_excel(resp.content)
    rename_columns = {col_name: 'name', col_phone: 'phone'}
    c: str = ''
    try:
        df.rename(columns={c: rename_columns[c.strip()] if c.strip() in rename_columns else c.strip() for c in df.columns},
                  inplace=True)
        df['name'] = df['name'].fillna('')
        return [
            User(tg_id=1, bad_user=True, name=u['name'], phone=u['phone'])
            for u in df.to_dict(orient='records')
        ]
    except Exception as ex:
        logger.exception(ex)
        return None


def merge_users(db_users: list[User], excel_users: list[User]) -> list[User]:
    merged = []
    for dbu in db_users:
        for exu in excel_users:
            if (exu.phone and dbu.phone and dbu.phone == exu.phone) \
                or (dbu.name and exu.name and dbu.name == exu.name) \
                and exu not in merged:
                exu.name = dbu.name
                exu.phone = dbu.phone
                exu.tg_id = dbu.tg_id
                merged.append(exu)
    logger.info('Merged {}, input users: {}'.format(len(merged), len(excel_users)))
    return merged
