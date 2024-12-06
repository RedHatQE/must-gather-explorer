from contextlib import redirect_stderr, redirect_stdout
import sys

from cmd2.utils import StdSim
from must_gather_explorer.utils import get_all_resources, get_all_yaml_and_log_files, read_aliases_file
import pytest
from must_gather_explorer.prompt_handler import MustGatherExplorerPrompt


def run_cmd(app, cmd):
    """Clear out and err StdSim buffers, run the command, and return out and err"""
    saved_sysout = sys.stdout
    sys.stdout = app.stdout

    # This will be used to capture app.stdout and sys.stdout
    copy_cmd_stdout = StdSim(app.stdout)

    # This will be used to capture sys.stderr
    copy_stderr = StdSim(sys.stderr)

    try:
        app.stdout = copy_cmd_stdout
        with redirect_stdout(copy_cmd_stdout):
            with redirect_stderr(copy_stderr):
                app.onecmd_plus_hooks(cmd)
    finally:
        app.stdout = copy_cmd_stdout.inner_stream
        sys.stdout = saved_sysout

    out = copy_cmd_stdout.getvalue()
    err = copy_stderr.getvalue()
    return out, err


@pytest.fixture(scope="module")
def aliases_file():
    yield read_aliases_file()


@pytest.fixture(scope="module")
def yaml_files():
    all_yaml_files, _ = get_all_yaml_and_log_files(
        must_gather_path="must_gather_explorer/tests/manifests/must-gather-data"
    )
    yield get_all_resources(all_yaml_files=all_yaml_files)


@pytest.fixture(scope="module")
def prompt_handler(aliases_file, yaml_files):
    app = MustGatherExplorerPrompt(aliases_file, yaml_files)
    app.onecmd_plus_hooks("set debug true")
    yield app


@pytest.mark.parametrize(
    "test_input",
    [
        ("get pod"),
        ("get pod csi-"),
        ("get pod csi-nfs-controller-c54d89cd5-gbd5s"),
        ("get pod -n kube-system"),
        ("get pod csi- -n kube-system"),
        ("get pod csi-nfs-controller-c54d89cd5-gbd5s -n kube-system"),
        ("get pod -oyaml"),
        ("get pod csi- -oyaml"),
        ("get pod csi-nfs-controller-c54d89cd5-gbd5s -oyaml"),
        ("get pod -oyaml -f spec.nodeSelector"),
        ("get pod csi- -oyaml -f spec.nodeSelector"),
        ("get pod csi-nfs-controller-c54d89cd5-gbd5s -oyaml -f spec.nodeSelector"),
    ],
)
def test_get(test_input, prompt_handler):
    _, err = run_cmd(prompt_handler, test_input)
    assert not err, err
