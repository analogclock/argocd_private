#!/bin/bash

echo "[python] Installing dependency update tool -- pur"
pip install virtualenv
virtualenv venv
. venv/bin/activate
pip install pur

echo "[python] Updating requirements*.txt dependencies"

# Find files based on requirements*.txt pattern, pass them to pur -r {file_name}
# using xargs command, one-by-one argument at a time (--max-lines=1)
find . -type f -name "requirements*.txt" | xargs --max-lines=1 pur -r

echo "[python] Finished the update"
