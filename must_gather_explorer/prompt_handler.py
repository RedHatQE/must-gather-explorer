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

    get_parser = cmd2.Cmd2ArgumentParser(description="get the must-gather data for a specific resource")
    get_parser.add_argument("get", help="Kind of the resource")
    get_parser.add_argument("args", nargs="*", help="Resource name or partial name")
    get_parser.add_argument(
        "-n", "--namespace", default="", choices_provider=namespaces, help="Namespace of the resource"
    )
    get_parser.add_argument("-oyaml", action="store_true", help="Output the must-gather data in YAML format")
    get_parser.add_argument(
        "-f",
        "--yaml-fields",
        default="",
        help="Print specified yaml field path, like .spec.source",
    )

    @cmd2.with_argparser(get_parser)
    def do_get(self, args: argparse.Namespace) -> None:
        """
        Get the must-gather data for a specific resource.
            Usage: get <resource_name> <options:resourcename|partialname>
            suported flags: -n <namespace>, -oyaml, -f <yaml_field_path>
        """
        yaml_fields = args.yaml_fields
        oyaml = args.oyaml
        if yaml_fields and not oyaml:
            CONSOLE.print("[red]yaml-fields can only be used with -oyaml flag")
            return

        list_of_args = args.args
        resource_name = ""
        if list_of_args:
            if len(list_of_args) > 1:
                CONSOLE.print(f"[red]Too many args {list_of_args}")
                return
            resource_name = list_of_args[0]

        must_gather_shell(
            action="get",
            kind=args.get,
            namespace=args.namespace,
            resource_name=resource_name,
            oyaml=oyaml,
            yaml_fields=yaml_fields,
            resources_aliases=self.resources_aliases,
            all_resources=self.all_resources,
        )

    do_EOF = do_exit
