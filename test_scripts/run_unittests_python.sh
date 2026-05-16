#!/bin/bash

UNRECOVERABLE_ERROR_EXIT_CODE=69

if ! command -v uv >/dev/null 2>&1; then
  echo "Error: uv is required but was not found."
  exit "$UNRECOVERABLE_ERROR_EXIT_CODE"
fi

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <source_build_folder>"
  exit 1
fi

SOURCE_FOLDER="$1"
WORKING_FOLDER=".tmp/python_${SOURCE_FOLDER//\//_}"

if [ ! -d "$SOURCE_FOLDER" ]; then
  echo "Error: source build folder '$SOURCE_FOLDER' does not exist."
  exit "$UNRECOVERABLE_ERROR_EXIT_CODE"
fi

rm -rf "$WORKING_FOLDER"
mkdir -p "$WORKING_FOLDER"
cp -R "$SOURCE_FOLDER"/. "$WORKING_FOLDER"/
echo "Copied from $SOURCE_FOLDER to $WORKING_FOLDER"

cd "$WORKING_FOLDER" 2>/dev/null
if [ $? -ne 0 ]; then
  echo "Error: could not enter working folder '$WORKING_FOLDER'."
  exit 2
fi

echo "Installing Python dependencies into isolated venv..."
uv venv --python 3.12 .venv || exit "$UNRECOVERABLE_ERROR_EXIT_CODE"
uv pip install --python .venv/bin/python -e . pytest pytest-cov || exit $?

echo "Running Python unit tests with pytest coverage..."
./.venv/bin/python -m pytest --cov=household_battery_management_env --cov-report=term-missing
exit $?
