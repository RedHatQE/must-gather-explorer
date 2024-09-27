import json
import shlex
import sys
from typing import Dict, List

import click
from pyhelper_utils.shell import run_command
from rich.console import Console

CONSOLE = Console()


@click.command("update-resources-aliases")
def fill_api_resources_aliases() -> None:
    command = "oc api-resources --no-headers=true"
    rc, out, err = run_command(command=shlex.split(command), verify_stderr=False, check=False, log_errors=False)
    if not rc:
        CONSOLE.print(f"Command {command} failed with error {err}")
        sys.exit(1)

    aliases_file_path = "app/manifests/aliases.json"

    try:
        with open(aliases_file_path) as aliases_file:
            resources_aliases = json.load(aliases_file)
    except Exception:
        resources_aliases = {}

    cli_resource_alias: Dict[str, List[str]] = {}

    for line in out.splitlines():
        # line example:
        # 'bindings                                    v1                true          Binding'
        # 'virtualmachines     vm,vms                  kubevirt.io/v1    true          VirtualMachine'

        split_line = line.split()

        # add NAME to the list of aliases
        alias_list: List[str] = [split_line[0]]  # alias_list = ['virtualmachines']

        line_len = len(split_line)

        # len is 5 when there are SHORTNAMES
        if line_len == 5:
            # add SHORTNAMES
            alias_list = alias_list + split_line[1].split(",")  # alias_list = ['virtualmachines','vm','vms']
        # len is 4 when there are NO SHORTNAMES
        elif line_len != 4:
            CONSOLE.print(f"split line should contain 4 or 5 elements, got {len(split_line): \nline: {split_line}}")
            sys.exit(1)

        # Fill cli_resource_alias dict with {Kind}:['alias1','alias2','...']
        cli_resource_alias[split_line[-1]] = (
            alias_list  # cli_resource_alias = {'VirtualMachine': ['virtualmachines','vm','vms']}
        )

    resources_aliases.update(cli_resource_alias)

    # Write to file
    with open(aliases_file_path, "w") as aliases_file:
        json.dump(resources_aliases, aliases_file, indent=4)


if __name__ == "__main__":
    fill_api_resources_aliases()
