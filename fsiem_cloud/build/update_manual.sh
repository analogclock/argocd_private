#!/bin/bash -e
#
# List files for manual updates and provide recomendations for how to update
# things manually. This file documents areas of this repo for which updates are
# not yet automated :p

cat << EOF
1. Build
   - Check build/versions.yaml file
   - Do NOT upgrade terraform beyond version 1.5.*, as license has changed
     since version 1.6
EOF
