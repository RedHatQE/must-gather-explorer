import json
import sysconfig
from pathlib import Path

from must_gather_explorer.constants import ALIASES_FILE_PATH, HOW_TO_UPDATE_ALIASES_MESSAGE, CONSOLE
from must_gather_explorer.exceptions import FailToReadJSONFileError


def get_aliases_file_path() -> str:
    if Path(ALIASES_FILE_PATH).exists():
        return ALIASES_FILE_PATH

    aliases_file_path = f"{sysconfig.get_paths()['purelib']}/{ALIASES_FILE_PATH}"

    if not Path(aliases_file_path).exists():
        raise FileNotFoundError(f"{aliases_file_path} file not found")

    return aliases_file_path


def read_aliases_file(raise_on_error: bool = True) -> dict[str, list[str]]:
    aliases_file_path = get_aliases_file_path()
    try:
        with open(aliases_file_path) as aliases_file:
            return json.load(aliases_file)

    except (FileNotFoundError, json.JSONDecodeError) as exp:
        if raise_on_error:
            CONSOLE.print(
                f"[bold red]Error:[/bold red] Can't read the aliases_file\n"
                f"Error details: {exp}\n"
                f"{HOW_TO_UPDATE_ALIASES_MESSAGE}"
            )
            raise FailToReadJSONFileError(file_name=aliases_file_path)
        return {}
