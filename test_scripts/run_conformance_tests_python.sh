#!/bin/bash

UNRECOVERABLE_ERROR_EXIT_CODE=69

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <build_folder> <conformance_tests_folder>"
  exit "$UNRECOVERABLE_ERROR_EXIT_CODE"
fi

BUILD_FOLDER="$1"
TESTS_FOLDER="$2"
CURRENT_DIR="$(pwd)"
WORKING_FOLDER=".tmp/python_${BUILD_FOLDER//\//_}"

if [ ! -d "$BUILD_FOLDER" ]; then
  echo "Error: build folder '$BUILD_FOLDER' does not exist."
  exit "$UNRECOVERABLE_ERROR_EXIT_CODE"
fi

if [ ! -d "$TESTS_FOLDER" ]; then
  echo "Error: conformance tests folder '$TESTS_FOLDER' does not exist."
  exit "$UNRECOVERABLE_ERROR_EXIT_CODE"
fi

if [ ! -d "$WORKING_FOLDER" ]; then
  echo "Error: prepared environment missing at '$WORKING_FOLDER'. Run prepare_environment_python.sh first."
  exit "$UNRECOVERABLE_ERROR_EXIT_CODE"
fi

if [ ! -x "$WORKING_FOLDER/.venv/bin/python" ]; then
  echo "Error: prepared Python virtual environment missing. Run prepare_environment_python.sh first."
  exit "$UNRECOVERABLE_ERROR_EXIT_CODE"
fi

"$WORKING_FOLDER/.venv/bin/python" - <<'PY'
import sys
raise SystemExit(0 if sys.version_info >= (3, 12) else 1)
PY
if [ $? -ne 0 ]; then
  echo "Error: prepared Python virtual environment must use Python 3.12 or newer."
  exit "$UNRECOVERABLE_ERROR_EXIT_CODE"
fi

cd "$WORKING_FOLDER" 2>/dev/null
if [ $? -ne 0 ]; then
  echo "Error: could not enter working folder '$WORKING_FOLDER'."
  exit "$UNRECOVERABLE_ERROR_EXIT_CODE"
fi

echo "Running Python conformance tests from $CURRENT_DIR/$TESTS_FOLDER..."
OUTPUT=$(./.venv/bin/python -m pytest "$CURRENT_DIR/$TESTS_FOLDER" --basetemp=./.pytest_tmp 2>&1)
EXIT_CODE=$?
echo "$OUTPUT"

if echo "$OUTPUT" | grep -Eq "collected 0 items|no tests ran"; then
  echo "Error: no conformance tests were discovered."
  exit 1
fi

exit "$EXIT_CODE"
