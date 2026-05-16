#!/bin/bash

UNRECOVERABLE_ERROR_EXIT_CODE=69

if ! command -v uv >/dev/null 2>&1; then
  echo "Error: uv is required but was not found."
  exit "$UNRECOVERABLE_ERROR_EXIT_CODE"
fi

BUILD_FOLDER="plain_modules/battery_management_env"
DEMO_SCRIPT="demo_project.py"
WORKING_FOLDER=".tmp/demo_python"

if [ ! -d "$BUILD_FOLDER" ]; then
  echo "Error: generated build folder '$BUILD_FOLDER' does not exist."
  echo "Run: codeplain battery_management_env.plain"
  exit "$UNRECOVERABLE_ERROR_EXIT_CODE"
fi

if [ ! -f "$DEMO_SCRIPT" ]; then
  echo "Error: demo script '$DEMO_SCRIPT' does not exist."
  exit "$UNRECOVERABLE_ERROR_EXIT_CODE"
fi

rm -rf "$WORKING_FOLDER"
mkdir -p "$WORKING_FOLDER"

echo "Preparing demo environment..."
uv venv --python 3.12 "$WORKING_FOLDER/.venv" || exit "$UNRECOVERABLE_ERROR_EXIT_CODE"
uv pip install --python "$WORKING_FOLDER/.venv/bin/python" -e "$BUILD_FOLDER" || exit "$UNRECOVERABLE_ERROR_EXIT_CODE"

echo "Running demo..."
"$WORKING_FOLDER/.venv/bin/python" "$DEMO_SCRIPT" "$@"
exit $?
