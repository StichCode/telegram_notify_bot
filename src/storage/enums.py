from enum import StrEnum


class StagesUser(StrEnum):
    start = 'start'
    mail = 'waiting'
    writing = 'writing'
    choose_column_s = 'choose_column_s'
    choose_column_e = 'choose_column_e'

    upload_file = 'upload_file'
    pre_send = 'pre_send'
    sending = 'sending'
    error = 'error'


class KeysStorage(StrEnum):
    stage = 'stage'
    message = 'message'
    column_name = 'column_name'
    file_path = 'file_path'
