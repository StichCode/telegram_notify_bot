from enum import StrEnum


class StagesUser(StrEnum):
    create_message = 'create_message'

    column_phone = 'column_phone'

    upload_file = 'upload_file'
    pre_send = 'pre_send'
    sending = 'sending'

    administration = 'administration'


class KeysStorage(StrEnum):
    stage = 'stage'
    message = 'message'

    column_phone = 'column_phone'
    file_path = 'file_path'


class CallbackKeys(StrEnum):
    create_admin = 'createAdmin'
    delete_admin = 'deleteAdmin'

    column_phone = 'columnPhone'

    sending = 'sending'
    cancel = 'cancel'

    accept_msg = 'acceptMsg'
    cancel_msg = 'cancelMsg'
