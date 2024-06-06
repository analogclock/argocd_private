#! /bin/sh -eu

echo "[python] [dev] Executing integration tests"
# -o log_cli=true/false  -- enable or disable logging, this is noisy
python -m pytest -o log_cli=false integration-tests
echo "[python] Done"
