#!/usr/bin/env python

from packaging.version import Version
import re
import requests
import subprocess
import shlex


def main() -> None:
    """
    Compare local running version against the latest version available on PyPI

    Prints a message if a newer version is available on PyPI.
    """
    try:
        uv_tree = subprocess.run(
            shlex.split("uv tree"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=30
        )
        matches = re.findall(r"must-gather-explorer v(\d+.\d+.\d+)", uv_tree.stdout.decode())
        if not matches:
            print("Error: Could not determine local version")
            return

        local_version = matches[0]

        response = requests.get("https://pypi.org/pypi/must-gather-explorer/json", timeout=30)
        response.raise_for_status()
        pypi_version = response.json()["info"]["version"]

        if Version(pypi_version) > Version(local_version):
            print(
                f"New version available: {pypi_version}, update by running: "
                "docker pull ghcr.io/redhatqe/must-gather-explorer:latest"
            )

    except Exception:
        print("Failed to check for updates")


if __name__ == "__main__":
    main()
