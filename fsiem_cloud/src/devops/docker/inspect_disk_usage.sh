#!/bin/bash

# Prints info about disk usage

set -e

# Require sudo
if [ "$(id -u)" != 0 ]; then echo "This script requires sudo: sudo $0 $*"; exit 1; fi

echo "----------------"
echo "Inspecting disk usage (top 50 dirs):"
du -h --max-depth=7  / | sort -h | tail -n 100
echo "----------------"
