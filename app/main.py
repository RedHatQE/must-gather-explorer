import os
from typing import Any, Dict, List

import click
import yaml


@click.command("must-gather-explorer")
@click.option(
    "kind",
    type=click.STRING,
    required=True,
    help="""
    \b
    The Kind of the resource to get from must-gather
    multiple kinds can be sent separated by comma (without spaces)
    Example: -k Deployment,Pod,ConfigMap
""",  # TODO do we want to get multiple kinds? Probably yes
)
@click.option(
    "-k",
    "--kind",
    type=click.STRING,
    required=True,
    help="""
    \b
    The Kind of the resource to get from must-gather
    multiple kinds can be sent separated by comma (without spaces)
    Example: -k Deployment,Pod,ConfigMap
""",  # TODO do we want to get multiple kinds? Probably yes
)
@click.option(
    "-name",
    "--name",
    type=click.STRING,
    default="",
    help="""
    \b
    The name, or the name prefix  of the resource to get from must-gather
""",
)
@click.option(
    "-n",
    "--namespace",
    type=click.STRING,
    default="",
    help="""
    \b
    The namespace of the resources to get from must-gather
""",
)
def main(
    kind: str,
    name: str,
    namespace: str,
) -> None:
    must_gather_path: str = "/home/jpeimer/Downloads/must-gather-cnv"

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
    # {Kind: [{”name”:”cdi-deployment”, : “path”: “path/../”, “namespace”: “openshift-cnv”}]}
    all_resources: Dict[str, Any] = {}
    # resource_dictionary = {}
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

    # Get resource using CLI (click) (reference in OCP wrapper - class generator)

    kinds: List[str] = kind.split(",")
    resources_list_requested: Dict[str, Any] = {}

    for kind in kinds:
        resources_list_requested.setdefault(kind, []).extend(
            get_cluster_resources(all_resources=all_resources, kind=kind, name=name, namespace=namespace)
        )


def get_cluster_resources(all_resources: Dict[str, Any], kind: str, name: str, namespace: str) -> List[Dict[str, Any]]:
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
