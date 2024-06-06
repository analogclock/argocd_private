#!/bin/bash -e

ROOT=$PWD
TF_DIR="src/terraform"
TF_LAMBDA_LIB_DIR="$ROOT/$TF_DIR/fsiem_benchmarking/python/lambda_layers/python"

mkdir -p $TF_LAMBDA_LIB_DIR
cd $TF_LAMBDA_LIB_DIR
pip install --quiet --upgrade -r $ROOT/$TF_DIR/fsiem_benchmarking/python/requirements.txt -t ./
cd ..
zip -r python_modules.zip .
