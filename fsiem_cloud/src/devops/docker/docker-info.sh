#!/bin/bash

# Prints info about docker instance

set -e

# Require sudo
if [ "$(id -u)" != 0 ]; then echo "This script requires sudo: sudo $0 $*"; exit 1; fi

echo "----------------"
echo "Inspecting docker environment"
echo "Available CPU: $(cat /sys/fs/cgroup/cpuset/cpuset.cpus)"
echo "Available RAM: $(free -h)"
docker version
docker info
echo "----------------"
