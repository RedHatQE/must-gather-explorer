#!/usr/bin/env bash

set -e -o pipefail
uv run python scripts/version_compare.py
uv run python must_gather_explorer/main.py -p /data
