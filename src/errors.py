class BadPhoneNumber(Exception):
    pass


class BadColumnName(Exception):
    def __init__(self, column: str):
        self.column = column
