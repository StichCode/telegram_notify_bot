from __future__ import print_function

import re
import prettytable as pt
import pandas as pd
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from loguru import logger

from config.config import GoogleExcelConfig


def _get_creds(credentials: str) -> Credentials:
    creds = service_account.Credentials.from_service_account_file(credentials)
    return creds


def _get_xlsx_from_google(cfg: GoogleExcelConfig):
    creds = _get_creds(cfg.credentials)
    try:
        service = build('sheets', 'v4', credentials=creds)
        # call the sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=cfg.sheet_id, range=cfg.range_name).execute()
        values = result.get('values', [])
        if not values:
            logger.error('No data found: {}'.format(result))
            return
        return values
    except Exception as ex:
        logger.exception(ex)


def get_prettify_data(cfg: GoogleExcelConfig) -> pt.PrettyTable | None:
    data = _get_xlsx_from_google(cfg=cfg)
    if not data:
        return None
    df = pd.DataFrame(data=data[1:], columns=cfg.const_columns)
    df = df.dropna()

    tb = pt.PrettyTable(['Название', 'Осталось мест'])

    for row in df.itertuples():
        if row and row.name and row.count != row.total:
            c = row.count if row.count else row.total
            name = row.name
            reg = re.search(r'\([а-яА-Я]+\)', name)
            if reg:
                name = name.replace(reg.group(), '').strip()
            tb.add_row([name, c])
    return tb
