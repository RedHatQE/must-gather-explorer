import cmd2
import argparse
from typing import Any

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
    example_parser.add_argument("-n", "--namespace", choices_provider=namespaces, help="Namespace of the resource")
    example_parser.add_argument("-k", "--kind", required=True, choices_provider=kinds, help="Kind of the resource")
    example_parser.add_argument("-oyaml", action="store_true", help="Output the must-gather data in YAML format")
    example_parser.add_argument("--name", help="Name of the resource or prefix of the name to search for")

    @cmd2.with_argparser(example_parser)
    def do_get(self, args: argparse.Namespace) -> None:
        """
        Get the must-gather data for a specific resource.
            Usage: get <resource_name>
            suported flags: -n <namespace>, -oyaml
        """
        must_gather_shell(
            user_command=f"get {args.kind} {f'-n {args.namespace}' if args.namespace else ''} {'-oyaml' if args.oyaml else ''} {args.name if args.name else ''}",
            resources_aliases=self.resources_aliases,
            all_resources=self.all_resources,
        )

    do_EOF = do_exit
