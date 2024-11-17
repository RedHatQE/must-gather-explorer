import json

from app.constants import ALIASES_FILE_PATH, HOW_TO_UPDATE_ALIASES_MESSAGE, CONSOLE
from app.exceptions import FailToReadJSONFileError


def read_aliases_file(raise_on_error: bool = True) -> dict[str, list[str]]:
    try:
        with open(ALIASES_FILE_PATH) as aliases_file:
            return json.load(aliases_file)

    except (FileNotFoundError, json.JSONDecodeError) as exp:
        if raise_on_error:
            CONSOLE.print(
                f"[bold red]Error:[/bold red] Can't read the aliases_file\n"
                f"Error details: {exp}\n"
                f"{HOW_TO_UPDATE_ALIASES_MESSAGE}"
            )
            raise FailToReadJSONFileError(file_name=ALIASES_FILE_PATH)
        return {}
