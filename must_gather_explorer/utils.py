import json
import os
import sysconfig
from pathlib import Path
from typing import Any

from rich.table import Table
from simple_logger.logger import get_logger
from tqdm import tqdm
import yaml

from must_gather_explorer.constants import ALIASES_FILE_PATH, HOW_TO_UPDATE_ALIASES_MESSAGE, CONSOLE
from must_gather_explorer.exceptions import FailToReadJSONFileError, MissingResourceKindAliasError


LOGGER = get_logger(__name__)
GET_ACTION_STR = "get"


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


def get_all_yaml_and_log_files(must_gather_path: str) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    all_yaml_files: dict[str, list[str]] = {}
    all_log_files: dict[str, list[str]] = {}
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
    if not all_yaml_files:
        CONSOLE.print(
            """
[red]Can't find any YAML files in the must-gather folder"
Please check that the --path points to the [bold]correct[/bold] and [bold]non-empty[/bold] must-gather folder
"""
        )

    return all_yaml_files, all_log_files


def get_all_resources(all_yaml_files: dict[str, list[str]]) -> dict[str, Any]:
    # Fill dictionaries for all resource kinds
    # {Kind: [{”name”:”cdi-deployment”, : “yaml_file”: “path/../”, “namespace”: “openshift-cnv”}]}
    all_resources: dict[str, Any] = {}
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
                    resource_dictionary = yaml.load(fd, Loader=yaml.CSafeLoader)
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

    return all_resources


def must_gather_shell(
    user_command: str, resources_aliases: dict[str, list[str]], all_resources: dict[str, Any]
) -> bool:
    """
    When this function return False it means that we continue if the loop in the main function
    """

    log_action_str = "logs"
    describe_action_str = "describe"

    actions_dict: dict[str, Any] = {
        GET_ACTION_STR: get_resources,
        log_action_str: get_logs,
        describe_action_str: get_describe,
    }

    commands_list: list[str] = user_command.split()
    action_name = commands_list[0]
    commands_list.remove(action_name)

    return parse_actions(
        commands_list=commands_list,
        action_name=action_name,
        actions_dict=actions_dict,
        resources_aliases=resources_aliases,
        all_resources=all_resources,
    )


def get_resources(resources_raw_data: list[dict[str, Any]], print_yaml: bool = False, **kwargs: dict[Any, Any]) -> None:
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


def print_resource_yaml(resources_raw_data: list[dict[str, Any]]) -> None:
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


def get_logs(**kwargs: dict[Any, Any]) -> bool:
    CONSOLE.print("Not implemented yet")
    return False


def get_describe(**kwargs: dict[Any, Any]) -> bool:
    CONSOLE.print("Not implemented yet")
    return False


def get_cluster_resources_raw_data(
    resources_aliases: Any, all_resources: dict[str, Any], kind: str, name: str, namespace: str
) -> list[dict[str, Any]]:
    resources_list: list[dict[str, Any]] = []

    resource_kind = get_resource_kind_by_alias(resources_aliases=resources_aliases, requested_kind=kind)

    for cluster_resource in all_resources.get(resource_kind, []):
        cluster_resource_name = cluster_resource.get("name")
        cluster_resource_namespace = cluster_resource.get("namespace")

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


def get_resource_kind_by_alias(resources_aliases: dict[str, list[str]], requested_kind: str) -> str:
    kind_lower = requested_kind.lower()

    for kind, aliases in resources_aliases.items():
        if kind == kind_lower or kind_lower in aliases:
            return kind

    CONSOLE.print(
        f"[bold red]Error:[/bold red] Not valid resource kind '{kind_lower}', "
        f"please make sure it was typed correctly and alias file is up to date\n"
        f"{HOW_TO_UPDATE_ALIASES_MESSAGE}"
    )
    raise MissingResourceKindAliasError(requested_kind=requested_kind)


def parse_actions(
    commands_list: list[str],
    action_name: str,
    actions_dict: dict[str, Any],
    resources_aliases: dict[str, list[str]],
    all_resources: dict[str, Any],
) -> bool:
    namespace_flag: str = "-n"
    namespace_name: str = ""

    if not commands_list:
        CONSOLE.print("Please pass the resource Kind")
        return False

    if namespace_flag in commands_list:
        namespace_index = commands_list.index(namespace_flag)
        namespace_name = commands_list[namespace_index + 1]
        commands_list.remove(namespace_flag)
        commands_list.remove(namespace_name)

    resource_kind = commands_list[0]
    commands_list.remove(resource_kind)

    # if "-oyaml" passed, change print_yaml to True
    # get pvc -n openshift-cnv -oyaml
    # get pvc -n openshift-cnv hpp -oyaml
    # get pvc -oyaml
    print_yaml = False
    yaml_flag = "-oyaml"
    if yaml_flag in commands_list:
        if action_name != GET_ACTION_STR:
            CONSOLE.print(f"'{yaml_flag}' is only supported with '{GET_ACTION_STR}' action")
            return False
        print_yaml = True
        commands_list.remove(yaml_flag)

    resource_name = ""
    if commands_list:
        if len(commands_list) > 1:
            CONSOLE.print("[red]Too many params passed in, run 'help' for help\n")
            return False
        resource_name = commands_list[0]

    try:
        resources_raw_data = get_cluster_resources_raw_data(
            resources_aliases=resources_aliases,
            all_resources=all_resources,
            kind=resource_kind,
            name=resource_name,
            namespace=namespace_name,
        )
        if not resources_raw_data:
            CONSOLE.print(f"No resources found for {resource_kind} {resource_name} {namespace_name}")
            return False
        actions_dict[action_name](resources_raw_data, print_yaml)

    except MissingResourceKindAliasError:
        return False
    return False
