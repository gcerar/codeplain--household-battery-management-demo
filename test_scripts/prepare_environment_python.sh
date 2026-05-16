#!/bin/bash

UNRECOVERABLE_ERROR_EXIT_CODE=69

if ! command -v uv >/dev/null 2>&1; then
  echo "Error: uv is required but was not found."
  exit "$UNRECOVERABLE_ERROR_EXIT_CODE"
fi

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <build_folder>"
  exit "$UNRECOVERABLE_ERROR_EXIT_CODE"
fi

BUILD_FOLDER="$1"
WORKING_FOLDER=".tmp/python_${BUILD_FOLDER//\//_}"

if [ ! -d "$BUILD_FOLDER" ]; then
  echo "Error: build folder '$BUILD_FOLDER' does not exist."
  exit "$UNRECOVERABLE_ERROR_EXIT_CODE"
fi

START_TIME=$(date +%s)

rm -rf "$WORKING_FOLDER"
mkdir -p "$WORKING_FOLDER"
cp -R "$BUILD_FOLDER"/. "$WORKING_FOLDER"/
echo "Copied from $BUILD_FOLDER to $WORKING_FOLDER"

cd "$WORKING_FOLDER" 2>/dev/null
if [ $? -ne 0 ]; then
  echo "Error: could not enter working folder '$WORKING_FOLDER'."
  exit "$UNRECOVERABLE_ERROR_EXIT_CODE"
fi

echo "Preparing isolated Python environment..."
uv venv --python 3.12 .venv || exit "$UNRECOVERABLE_ERROR_EXIT_CODE"
uv pip install --python .venv/bin/python -e . pytest || exit "$UNRECOVERABLE_ERROR_EXIT_CODE"

END_TIME=$(date +%s)
echo "Python environment prepared in $((END_TIME - START_TIME)) seconds."
