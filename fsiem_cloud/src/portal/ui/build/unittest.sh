#!/bin/bash

# -e => exit on error
set -e

# install node modules
npm install --no-fund

# run full test suite, the output is noisy save it to a file
echo "[ui] Running unit tests"
npm run test:all
