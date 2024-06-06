#!/bin/sh -eu

echo "[python] [dev] Executing unit tests"
# -o log_cli=true/false  -- enable or disable logging, this is noisy
# --cov                  -- test coverate and reports
python3 -m pytest -o log_cli=false --cov --cov-report=html --ignore=integration-tests
echo "[python] Done"
