from __future__ import print_function

import re
from pathlib import Path
import prettytable as pt
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from loguru import logger

from config.config import GoogleExcelConfig


def _valid_auth(cfg: GoogleExcelConfig) -> Credentials:
    creds = None
    tok = Path(cfg.token)
    creds_file = Path(cfg.credentials)
    if tok.exists():
        creds = Credentials.from_authorized_user_file(tok, cfg.scopes)
    if creds and not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    elif not creds:
        flow = InstalledAppFlow.from_client_secrets_file(creds_file, cfg.scopes)
        creds = flow.run_local_server(port=0)
    with open(tok, 'w') as tk_file:
        tk_file.write(creds.to_json())
    return creds


def _get_xlsx_from_google(cfg: GoogleExcelConfig):
    creds = _valid_auth(cfg)
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
