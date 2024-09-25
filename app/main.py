import os
import sys
from typing import Any, Dict, List

import click
import yaml
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

CONSOLE = Console()

NAMESPACE_FLAG = "-n"


@click.command("must-gather-explorer")
@click.option(
    "-p",
    "--path",
    type=click.Path(exists=True),
    help="""
    \b
    The full path to the must-gather folder
""",
)
def main(
    path: str,
) -> None:
    must_gather_path = path

    CONSOLE.print(
        "\n[bold cyan]Welcome to the must-gather-explorer\n" "Please wait while the must gather data is being parsed\n"
    )

    # Fill dictionaries for all files kinds
    all_yaml_files: Dict[str, List[str]] = {}
    all_log_files: Dict[str, List[str]] = {}
    for root, dirs, _ in os.walk(must_gather_path):
        for _dir in dirs:
            for _file in os.listdir(os.path.join(root, _dir)):
                file_extention = _file.rsplit(".", 1)
                #  print(f"{_file=}, {file_extention[-1]=}")
                if file_extention[-1] in ("yaml", "yml"):
                    # print(os.path.join(root, _dir, _file))
                    all_yaml_files.setdefault(os.path.join(root, _dir), []).append(_file)

                # Poa may have several containers, the path to the log is:
                # <path>/namespaces/openshift-ovn-kubernetes/pods/ovnkube-node-6vrt6/kubecfg-setup/kubecfg-setup/logs
                # <path>/namespaces/openshift-ovn-kubernetes/pods/ovnkube-node-6vrt6/kube-rbac-proxy-node/kube-rbac-proxy-node/logs
                elif file_extention[-1] == "log":
                    all_log_files.setdefault(os.path.join(root, _dir), []).append(_file)

    # Fill dictionaries for all resource kinds
    # {Kind: [{”name”:”cdi-deployment”, : “yaml_file”: “path/../”, “namespace”: “openshift-cnv”}]}
    all_resources: Dict[str, Any] = {}
    for yaml_path, yaml_files in all_yaml_files.items():
        for yaml_file in yaml_files:
            yaml_file_path = os.path.join(yaml_path, yaml_file)
            with open(yaml_file_path) as fd:
                resource_dictionary = yaml.safe_load(fd)
            resource_dict_metadata = resource_dictionary["metadata"]
            all_resources.setdefault(resource_dictionary["kind"], []).append({
                "name": resource_dict_metadata.get("name", ""),
                "namespace": resource_dict_metadata.get("namespace", ""),
                "yaml_file": yaml_file_path,
            })
    if not all_resources:
        CONSOLE.print(
            "[red]Can't parse the files \n"
            "Please check that the --path points to the [bold]correct[/bold] and [bold]non-empty[/bold] must-gather folder"
        )
        sys.exit(1)

    actions_dict: Dict[str, Any] = {
        "get": get_resources,
        "logs": get_logs,
        "describe": get_describe,
        "exit": None,
        "help": None,
    }

    # Get user prompt
    while True:
        user_command = Prompt.ask("Enter the command ")

        # get PersistentVolumeClaim -n openshift-cnv
        # get PersistentVolumeClaim -n openshift-cnv hpp
        # get PersistentVolumeClaim hpp
        # get PersistentVolumeClaim

        commands_list: List[str] = user_command.split()

        action_name = commands_list[0]
        commands_list.remove(action_name)

        supported_actions = actions_dict.keys()
        if action_name not in supported_actions:
            CONSOLE.print(f"Action '{action_name}' is not supported, please use a supported action {supported_actions}")
            continue

        if action_name == "exit":
            sys.exit(0)

        if action_name == "help":
            print_help()
            continue

        namespace_name = ""
        if NAMESPACE_FLAG in commands_list:
            namespace_index = commands_list.index(NAMESPACE_FLAG)
            namespace_name = commands_list[namespace_index + 1]
            commands_list.remove(NAMESPACE_FLAG)
            commands_list.remove(namespace_name)

        if not commands_list:
            CONSOLE.print("Please pass the resource Kind")
            continue

        resource_kind = commands_list[0]
        commands_list.remove(resource_kind)

        resource_name = ""

        if commands_list:
            if len(commands_list) > 1:
                CONSOLE.print("[red]Too many params passed in, run 'help' for help\n")
                continue

            resource_name = commands_list[0]

        resources_raw_data = get_cluster_resources_raw_data(
            all_resources=all_resources, kind=resource_kind, name=resource_name, namespace=namespace_name
        )
        actions_dict[action_name](resources_raw_data)


def get_resources(resources_raw_data: List[Dict[str, Any]]) -> None:
    # TODO Hande when no resource found, i.e. "get VirtualMachine"

    # Print table of Namespace, Name
    table = Table()
    table.add_column("NAMESPACE")
    table.add_column("NAME")

    for raw_data in resources_raw_data:
        table.add_row(raw_data["namespace"], raw_data["name"])

    CONSOLE.print(table)


def get_logs() -> None:
    pass


def get_describe() -> None:
    pass


def print_help() -> None:
    pass


def get_cluster_resources_raw_data(
    all_resources: Dict[str, Any], kind: str, name: str, namespace: str
) -> List[Dict[str, Any]]:
    resources_list: List[Dict[str, Any]] = []

    for cluster_resource in all_resources[kind]:
        cluster_resource_name = cluster_resource.get("name")
        cluster_resource_namespace = cluster_resource.get("namespace")

        # kind, name, namespace
        if name and namespace:
            if (
                cluster_resource_namespace == namespace
                and cluster_resource_name
                and cluster_resource_name.startswith(name)
            ):
                resources_list.append(cluster_resource)

        # kind, name
        elif name:
            if cluster_resource_name and cluster_resource_name.startswith(name):
                resources_list.append(cluster_resource)

        # kind, namespace
        elif namespace:
            if cluster_resource_namespace == namespace:
                resources_list.append(cluster_resource)

        # kind (mandatory)
        else:
            resources_list.append(cluster_resource)

    return resources_list


if __name__ == "__main__":
    main()
