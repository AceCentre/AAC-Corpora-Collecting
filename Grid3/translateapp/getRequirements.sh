#!/bin/bash

echo "Updating requirements.txt"
uv sync
uv pip compile pyproject.toml -o requirements.txt >/dev/null
echo "-e ." >>requirements.txt
echo "Successfully updated requirements.txt"