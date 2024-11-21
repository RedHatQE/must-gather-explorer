import os

import sys
from functools import lru_cache
from typing import Any, Dict, List
from pathlib import Path
from tqdm import tqdm
import click
import yaml
from rich.prompt import Prompt
from rich.table import Table

from must_gather_explorer.constants import HOW_TO_UPDATE_ALIASES_MESSAGE, CONSOLE
from must_gather_explorer.exceptions import MissingResourceKindAliasError, FailToReadJSONFileError
from must_gather_explorer.utils import read_aliases_file
from simple_logger.logger import get_logger

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
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logs")
def main(path: str, verbose: bool) -> None:
    if verbose:
        LOGGER.setLevel("DEBUG")

    must_gather_path = path

    CONSOLE.print(
        """
[bold cyan]Welcome to the must-gather-explorer
Please wait while the must gather data is being parsed

"""
    )

    # Fill dictionaries for all files kinds
    all_yaml_files: Dict[str, List[str]] = {}
    all_log_files: Dict[str, List[str]] = {}
    for root, dirs, _ in Path(must_gather_path).walk():
        for _dir in dirs:
            _dir_path = Path(root, _dir)
            for _file in _dir_path.iterdir():
                if _file.is_dir():
                    continue

                file_extention = _file.suffix
                if not file_extention:
                    LOGGER.debug(f"Skipping file {_file}, file has no extension")
                    continue

                if file_extention in (".yaml", ".yml"):
                    all_yaml_files.setdefault(str(_dir_path), []).append(_file.name)

                # Pod may have several containers, the path to the log is:
                # <path>/namespaces/openshift-ovn-kubernetes/pods/ovnkube-node-6vrt6/kubecfg-setup/kubecfg-setup/logs
                # <path>/namespaces/openshift-ovn-kubernetes/pods/ovnkube-node-6vrt6/kube-rbac-proxy-node/kube-rbac-proxy-node/logs
                elif file_extention == ".log":
                    all_log_files.setdefault(str(_dir_path), []).append(_file.name)

    # Fill dictionaries for all resource kinds
    # {Kind: [{”name”:”cdi-deployment”, : “yaml_file”: “path/../”, “namespace”: “openshift-cnv”}]}

    all_resources: Dict[str, Any] = {}
    for yaml_path, yaml_files in tqdm(
        all_yaml_files.items(),
        desc="Parsing data",
        colour="green",
        dynamic_ncols=True,
    ):
        for yaml_file in yaml_files:
            yaml_file_path = Path(yaml_path, yaml_file)

            with open(yaml_file_path) as fd:
                try:
                    resource_dictionary = yaml.safe_load(fd)
                except yaml.constructor.ConstructorError as exp:
                    LOGGER.debug(f"Error parsing YAML file {yaml_file_path}: {exp}")
                    continue

            resource_dict_metadata = resource_dictionary["metadata"]
            all_resources.setdefault(resource_dictionary["kind"].lower(), []).append({
                "name": resource_dict_metadata.get("name", ""),
                "namespace": resource_dict_metadata.get("namespace", ""),
                "yaml_file": yaml_file_path,
            })

    if not all_resources:
        CONSOLE.print(
            """
[red]Can't parse the files"
Please check that the --path points to the [bold]correct[/bold] and [bold]non-empty[/bold] must-gather folder
"""
        )
        sys.exit(1)

    get_action = "get"

    actions_dict: Dict[str, Any] = {
        get_action: get_resources,
        "logs": get_logs,
        "describe": get_describe,
        "exit": None,
        "help": None,
    }

    # Get user prompt
    while True:
        user_command: str = Prompt.ask("Command")
        if not user_command:
            continue

        # get PersistentVolumeClaim -n openshift-cnv
        # get PersistentVolumeClaim -n openshift-cnv hpp
        # get PersistentVolumeClaim hpp
        # get PersistentVolumeClaim

        commands_list: List[str] = user_command.split()

        action_name = commands_list[0]
        supported_actions = actions_dict.keys()

        if action_name not in supported_actions:
            CONSOLE.print(
                f"""
Action '{action_name}' is not supported, please use a supported action:
    {"\n    ".join(supported_actions)}
"""
            )
            continue

        commands_list.remove(action_name)

        if action_name == "exit":
            sys.exit(0)

        if action_name == "help":
            print_help()
            continue

        namespace_flag: str = "-n"
        namespace_name: str = ""
        if namespace_flag in commands_list:
            namespace_index = commands_list.index(namespace_flag)
            namespace_name = commands_list[namespace_index + 1]
            commands_list.remove(namespace_flag)
            commands_list.remove(namespace_name)

        if not commands_list:
            CONSOLE.print("Please pass the resource Kind")
            continue

        resource_kind = commands_list[0]
        commands_list.remove(resource_kind)

        # if "-oyaml" passed, change print_yaml to True
        # get pvc -n openshift-cnv -oyaml
        # get pvc -n openshift-cnv hpp -oyaml
        # get pvc -oyaml
        print_yaml = False
        yaml_flag = "-oyaml"
        if yaml_flag in commands_list:
            if action_name != get_action:
                CONSOLE.print(f"'{yaml_flag}' is only supported with '{get_action}' action")
                continue
            print_yaml = True
            commands_list.remove(yaml_flag)

        resource_name = ""
        if commands_list:
            if len(commands_list) > 1:
                CONSOLE.print("[red]Too many params passed in, run 'help' for help\n")
                continue
            resource_name = commands_list[0]

        try:
            resources_raw_data = get_cluster_resources_raw_data(
                all_resources=all_resources, kind=resource_kind, name=resource_name, namespace=namespace_name
            )
            if not resources_raw_data:
                CONSOLE.print(f"No resources found for {resource_kind} {resource_name} {namespace_name}")
                continue
            actions_dict[action_name](resources_raw_data, print_yaml)

        except FailToReadJSONFileError:
            sys.exit(1)
        except MissingResourceKindAliasError:
            continue


def get_resources(resources_raw_data: List[Dict[str, Any]], print_yaml: bool = False, **kwargs: Dict[Any, Any]) -> None:
    if print_yaml:
        print_resource_yaml(resources_raw_data=resources_raw_data)
    else:
        # Print table of Namespace, Name
        table = Table()
        table.add_column("NAMESPACE")
        table.add_column("NAME")
        for raw_data in resources_raw_data:
            table.add_row(raw_data["namespace"], raw_data["name"])
        CONSOLE.print(table)


def print_resource_yaml(resources_raw_data: List[Dict[str, Any]]) -> None:
    for raw_data in resources_raw_data:
        # Read resource yaml file from path in raw_data["yaml_file"]
        try:
            with open(raw_data["yaml_file"]) as fd:
                resource_yaml_content = fd.read()
        except (FileNotFoundError, IOError) as e:
            CONSOLE.print(f"[red]Error opening file {raw_data['yaml_file']}: {e}")
            continue

        CONSOLE.print(resource_yaml_content)
        CONSOLE.print("-" * os.get_terminal_size().columns)


def get_logs(**kwargs: Dict[Any, Any]) -> None:
    pass


def get_describe(**kwargs: Dict[Any, Any]) -> None:
    pass


def print_help(**kwargs: Dict[Any, Any]) -> None:
    pass


def get_cluster_resources_raw_data(
    all_resources: Dict[str, Any], kind: str, name: str, namespace: str
) -> List[Dict[str, Any]]:
    resources_list: List[Dict[str, Any]] = []

    resource_kind = get_resource_kind_by_alias(requested_kind=kind)

    for cluster_resource in all_resources.get(resource_kind, []):
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


@lru_cache
def get_resource_kind_by_alias(requested_kind: str) -> str:
    kind_lower = requested_kind.lower()

    resources_aliases = read_aliases_file()

    for kind, aliases in resources_aliases.items():
        if kind == kind_lower or kind_lower in aliases:
            return kind

    CONSOLE.print(
        f"[bold red]Error:[/bold red] Not valid resource kind '{kind_lower}', "
        f"please make sure it was typed correctly and alias file is up to date\n"
        f"{HOW_TO_UPDATE_ALIASES_MESSAGE}"
    )
    raise MissingResourceKindAliasError(requested_kind=requested_kind)


if __name__ == "__main__":
    main()
