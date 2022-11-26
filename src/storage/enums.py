from enum import StrEnum


class StagesUser(StrEnum):
    create_message = 'create_message'

    choose_column_s = 'choose_column_s'
    choose_column_e = 'choose_column_e'

    column_name = 'columns_ids'
    column_phone = 'column_phone'

    upload_file = 'upload_file'
    pre_send = 'pre_send'
    sending = 'sending'

    administration = 'administration'
    error = 'error'


class KeysStorage(StrEnum):
    stage = 'stage'
    message = 'message'
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

    accept_phone = 'accept_id'
    cancel_phone = 'cancel_id'

    accept_name = 'accept_name'
    cancel_name = 'cancel_name'
