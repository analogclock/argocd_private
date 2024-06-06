#! /bin/bash

# -e => exit on error
set -e

# Run dotnet tests
echo "[portal-api] Running unit tests"
dotnet test src/tests/unit/FinsProvisioning.Tests -warnaserror
