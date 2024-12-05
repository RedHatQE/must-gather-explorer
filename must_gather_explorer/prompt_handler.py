import cmd2
import argparse
from typing import Any

from must_gather_explorer.constants import CONSOLE
from must_gather_explorer.utils import must_gather_shell


class MustGatherExplorerPrompt(cmd2.Cmd):
    prompt = "must-gather-explorer > "
    intro = "\nWelcome to must-gather-explorer. Type `?` to list commands.\n"

    def __init__(
        self, resources_aliases: dict[str, list[str]], all_resources: dict[str, Any], *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.all_resources = all_resources
        self.resources_aliases = resources_aliases
        # self.hidden_commands.append("EOF")

    def do_exit(self, inp: str) -> bool:
        """
        Exit the program.
        """
        return True

    def namespaces(self) -> list[str]:
        namespaces: list[str] = []
        for resources in self.all_resources.values():
            for resource in resources:
                _namespace = resource.get("namespace")
                if _namespace and _namespace not in namespaces:
                    namespaces.append(_namespace)

        return namespaces

    def kinds(self) -> list[str]:
        return list(
            set(
                list(self.resources_aliases.keys())
                + [kind for kinds in self.resources_aliases.values() for kind in kinds]
            )
        )

    example_parser = cmd2.Cmd2ArgumentParser(description="get the must-gather data for a specific resource")
    example_parser.add_argument("get", help="Kind of the resource")
    example_parser.add_argument("args", nargs="*", help="Resource name or partial name")
    example_parser.add_argument("-n", "--namespace", choices_provider=namespaces, help="Namespace of the resource")
    example_parser.add_argument("-oyaml", action="store_true", help="Output the must-gather data in YAML format")
    example_parser.add_argument(
        "-f", "--yaml-fields", default="", help="Print specified yaml field path, like .spec.source"
    )

    @cmd2.with_argparser(example_parser)
    def do_get(self, args: argparse.Namespace) -> None:
        """
        Get the must-gather data for a specific resource.
            Usage: get <resource_name>
            suported flags: -n <namespace>, -oyaml
        """
        list_of_args = args.args
        resource_name = ""
        if list_of_args:
            # supported args: resource name and yaml fields path like .spec.source
            if len(list_of_args) > 2:
                CONSOLE.print(f"Too many args {list_of_args}")
                return
            resource_name = list_of_args[0]

        # TODO pass user_command as the separate arguments
        must_gather_shell(
            user_command=f"get {args.get} {f'-n {args.namespace}' if args.namespace else ''} {resource_name} {'-oyaml' if args.oyaml else ''} {args.yaml_fields}",
            resources_aliases=self.resources_aliases,
            all_resources=self.all_resources,
        )

    do_EOF = do_exit
