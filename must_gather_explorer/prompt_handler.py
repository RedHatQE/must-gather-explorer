from cmd import Cmd
from typing import Any

from must_gather_explorer.utils import must_gather_shell


class MustGatherExplorerPrompt(Cmd):
    prompt = "must-gather-explorer > "
    intro = "\nWelcome to must-gather-explorer. Type? to list commands.\n"

    def __init__(self, resources_aliases: dict[str, list[str]], all_resources: dict[str, Any]) -> None:
        super().__init__()
        self.all_resources = all_resources
        self.resources_aliases = resources_aliases

    def do_exit(self, inp: str) -> bool:
        """
        Exit the program.
        """
        return True

    def do_get(self, inp: str) -> None:
        """
        Get the must-gather data for a specific resource.
            Usage: get <resource_name>
            suported flags: -n <namespace>, -oyaml
        """
        must_gather_shell(
            user_command=f"get {inp}",
            resources_aliases=self.resources_aliases,
            all_resources=self.all_resources,
        )

    do_EOF = do_exit
