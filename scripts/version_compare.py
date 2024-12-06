#!/usr/bin/env python

from packaging.version import Version
import re
import requests
import subprocess
import shlex


def main() -> None:
    """
    Compare local running version agains the latest version available on Pypi

    Returns:
        bool: True if Pypi version is greater than local version, False otherwise.
    """
    uv_tree = subprocess.run(shlex.split("uv tree"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    local_version = re.findall(r"must-gather-explorer v(\d.\d.\d)", uv_tree.stdout.decode())[0]
    pypi_version = requests.get("https://pypi.org/pypi/must-gather-explorer/json").json()["info"]["version"]

    if Version(pypi_version) > Version(local_version):
        print(
            f"New version available: {pypi_version}, update by runing: docker pull ghcr.io/redhatqe/must-gather-explorer:latest"
        )


if __name__ == "__main__":
    main()
