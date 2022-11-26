from enum import StrEnum


class StagesUser(StrEnum):
    start = 'start'
    mail = 'waiting'
    writing = 'writing'
    choose_column_s = 'choose_column_s'
    choose_column_e = 'choose_column_e'

    column_ids = 'columns_ids'
    column_phone = 'column_phone'

    upload_file = 'upload_file'
    pre_send = 'pre_send'
    sending = 'sending'

    administration = 'administration'
    error = 'error'


class KeysStorage(StrEnum):
    stage = 'stage'
    message = 'message'
    column_id = 'column_id'
    column_phone = 'column_id'

    column_name = 'column_name'
    file_path = 'file_path'


class CallbackKeys(StrEnum):
    create_admin = 'create_admin'
    delete_admin = 'delete_admin'

    sending = 'sending'
    cancel = 'cancel'

    accept_msg = 'accept_msg'
    cancel_msg = 'cancel_msg'

    accept_id = 'accept_id'
    cancel_id = 'cancel_id'

    accept_name = 'accept_name'
    cancel_name = 'cancel_name'
