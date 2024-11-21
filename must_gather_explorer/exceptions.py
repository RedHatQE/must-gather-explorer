class MissingResourceKindAliasError(Exception):
    def __init__(self, requested_kind: str) -> None:
        self.requested_kind = requested_kind

    def __repr__(self) -> str:
        return f"Resource kind alias '{self.requested_kind}' not found"


class FailToReadJSONFileError(Exception):
    def __init__(self, file_name: str) -> None:
        self.file_name = file_name

    def __repr__(self) -> str:
        return f"Can't read file '{self.file_name}'"
