import sys

import click
from pyhelper_utils.runners import function_runner_with_pdb
from simple_logger.logger import get_logger

from must_gather_explorer.constants import CONSOLE, HOW_TO_UPDATE_ALIASES_MESSAGE
from must_gather_explorer.exceptions import FailToReadJSONFileError
from must_gather_explorer.prompt_handler import MustGatherExplorerPrompt
from must_gather_explorer.utils import (
    get_all_resources,
    get_all_yaml_and_log_files,
    read_aliases_file,
)

LOGGER = get_logger(__name__)


@click.command("must-gather-explorer")
@click.option(
    "-p",
    "--path",
    type=click.Path(exists=True),
    required=True,
    help="""
    \b
    The full path to the must-gather folder
""",
)
@click.option(
    "--pdb",
    help="Drop to `ipdb` shell on exception",
    is_flag=True,
    show_default=True,
)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logs")
def main(path: str, verbose: bool, pdb: bool) -> None:
    if verbose:
        LOGGER.setLevel("DEBUG")

    must_gather_path = path

    CONSOLE.print(
        """
[bold cyan]Welcome to the must-gather-explorer
Please wait while the must gather data is being parsed

"""
    )

    # Fail fast if the aliases file is missing
    try:
        resources_aliases = read_aliases_file()
    except (FailToReadJSONFileError, FileNotFoundError):
        CONSOLE.print(f"[red]Can't read aliases file, {HOW_TO_UPDATE_ALIASES_MESSAGE}\n")
        sys.exit(1)

    all_yaml_files, all_log_files = get_all_yaml_and_log_files(must_gather_path=must_gather_path)  # noqa F841
    if not all_yaml_files:
        sys.exit(1)

    all_resources = get_all_resources(all_yaml_files=all_yaml_files)

    if not all_resources:
        sys.exit(1)

    sys.argv = [sys.argv[0]]  # Remove all cick options from sys.argv
    sys.exit(MustGatherExplorerPrompt(resources_aliases=resources_aliases, all_resources=all_resources).cmdloop())


if __name__ == "__main__":
    function_runner_with_pdb(func=main)
