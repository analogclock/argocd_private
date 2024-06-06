#!/bin/bash -e

# Assume we start from src/python/lambda_layer
LAMBDA_ARTIFACTS_DIR="artifacts"
TMP_LAMBDA_LAYER="$LAMBDA_ARTIFACTS_DIR/python"
NEXUS_PYPI_URL=${NEXUS_PYPI_URL:-https://pypi.org/simple}

echo "Creating lambda layer for fsiem_api_client"
echo "* * * * *"

echo "Installing fsiem_api_client lambda layer into $TMP_LAMBDA_LAYER"
echo "From pip repo: $NEXUS_PYPI_URL"
pip install --upgrade --quiet --index-url ${NEXUS_PYPI_URL} -r requirements-layers.txt -t $TMP_LAMBDA_LAYER
pushd $LAMBDA_ARTIFACTS_DIR
echo "Zipping $TMP_LAMBDA_LAYER into layer_fsiem_api_client.zip"
zip -rqq "layer_fsiem_api_client.zip" "python"
echo "Clearing $TMP_LAMBDA_LAYER"
find python -mindepth 1 -delete > /dev/null
popd

echo "Done"
