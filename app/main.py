import os
from typing import Dict, List

import ipdb
import yaml


def main():
    must_gather_path: str = "/home/jpeimer/Downloads/must-gather-cnv"

    # Fill dictionaries for all files kinds
    all_yaml_files: Dict[str, List[str]] = {}
    all_log_files: Dict[str, List[str]] = {}
    for root, dirs, files in os.walk(must_gather_path):
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
    all_resources: Dict[str, str] = {}
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

    # ipdb.set_trace()

    # Get resource using CLI (click) (reference in OCP wrapper - class generator)
    resources_list = get_cluster_resources(
        all_resources=all_resources, kind="PersistentVolumeClaim", name="hpp", namespace="openshift-cnv"
    )
    ipdb.set_trace()


def get_cluster_resources(all_resources, kind, name=None, namespace=None):
    resources_list: List[Dict] = []

    for cluster_resource in all_resources[f"{kind}"]:
        if (
            cluster_resource.get("namespace") == namespace
            and cluster_resource.get("name")
            and cluster_resource.get("name").startswith(name)
        ):
            resources_list.append(cluster_resource)
    return resources_list


if __name__ == "__main__":
    main()
