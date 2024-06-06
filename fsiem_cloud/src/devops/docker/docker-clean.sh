#!/bin/bash

# Deletes all cached resources associated with docker: images, stopped containers,
# unused networks, etc

set -e

# Require sudo
if [ "$(id -u)" != 0 ]; then echo "This script requires sudo: sudo $0 $*"; exit 1; fi

echo "Pruning docker system"
docker system prune -af
echo "Done"
