import sys

from must_gather_explorer.tests.constants import MUST_GATHER_PATH_FOR_TESTS
from must_gather_explorer.utils import (
    get_aliases_file_path,
    read_aliases_file,
    get_all_yaml_and_log_files,
    get_all_resources,
    get_resources,
    get_cluster_resources_raw_data,
    get_resource_kind_by_alias,
)

from io import StringIO


class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


def test_get_aliases_file_path():
    get_aliases_file_path()


def test_read_aliases_file():
    assert read_aliases_file()


def test_get_all_yaml_and_log_files():
    all_yaml_files, all_log_files = get_all_yaml_and_log_files(must_gather_path=MUST_GATHER_PATH_FOR_TESTS)
    assert all_yaml_files, "No yaml files found"
    assert all_log_files, "No log files found"


def test_get_all_resources():
    all_yaml_files, _ = get_all_yaml_and_log_files(must_gather_path=MUST_GATHER_PATH_FOR_TESTS)
    all_resources_dict = get_all_resources(all_yaml_files=all_yaml_files)

    for pod in all_resources_dict["pod"]:
        assert pod.get("name"), f"Pod name is missing: {pod}"
        assert pod.get("namespace"), f"Pod namespace is missing: {pod}"
        assert pod.get("yaml_file"), f"Pod yaml_file is missing: {pod}"

    # TODO: add test for all_log_files


def test_get_resource_kind_by_alias():
    assert get_resource_kind_by_alias(resources_aliases=read_aliases_file(), requested_kind="Pod")


# TODO add parameters for different querries (pod, node, with yaml, with yaml fields, with name, with partial name)
def test_get_resources():
    all_yaml_files, _ = get_all_yaml_and_log_files(must_gather_path=MUST_GATHER_PATH_FOR_TESTS)
    all_resources_dict = get_all_resources(all_yaml_files=all_yaml_files)
    aliases = read_aliases_file()
    cluster_resources_raw_data = get_cluster_resources_raw_data(
        all_resources=all_resources_dict, resources_aliases=aliases, kind="pod"
    )

    with Capturing() as output:
        get_resources(resources_raw_data=cluster_resources_raw_data)

    output_string = "\n".join(output)

    for item in ("NAMESPACE", "NAME", "kube-system", "csi-nfs-controller-c54d89cd5-gbd5s", "csi-nfs-node-2r5tx"):
        assert item in output_string
