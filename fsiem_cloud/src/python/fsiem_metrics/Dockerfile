ARG DOCKER_REGISTRY=""
ARG DOCKER_PYTHON_VERSION
FROM ${DOCKER_REGISTRY}python:${DOCKER_PYTHON_VERSION}

ARG NEXUS_PYPI_URL

WORKDIR /app/fsiem_metrics
COPY ./fsiem_metrics .
COPY ./fsiem_api_client /app/fsiem_api_client

ENV SERIAL_NUMBER=""
ENV DYNAMODB_ACTIVATION_TABLE=""
ENV DYNAMODB_METRICS_STORAGE_TABLE=""
ENV DYNAMODB_REGION=""
ENV S3_BUCKET=""
ENV S3_DIR=""
ENV REGION=""

RUN set -eux && \
  pip3 install -r requirements.txt --index-url ${NEXUS_PYPI_URL} --quiet && \
  pip3 install -r requirements-unittest.txt --index-url ${NEXUS_PYPI_URL} --quiet && \
  ./build/unittest.sh && \
  pip3 uninstall -y --quiet -r requirements-unittest.txt && \
  pip3 uninstall -y setuptools coverage pip > /dev/null && \
  rm -rf /root/.cache/pip && \
  find / | grep -E "(/__pycache__$|\.pyc$|\.pyo|\.exe$)" | xargs rm -rf && \
  BOTO_DATA=/usr/local/lib/python3.11/site-packages/botocore/data && \
  find $BOTO_DATA | grep examples-1.json | xargs rm -rf && \
  find $BOTO_DATA/ec2        -mindepth 1 -type d | sort -r | tail -n +2 | xargs rm -rf && \
  find $BOTO_DATA/cloudfront -mindepth 1 -type d | sort -r | tail -n +2 | xargs rm -rf && \
  rm -rf $BOTO_DATA/sagemaker $BOTO_DATA/rds $BOTO_DATA/mediaconvert

ENTRYPOINT python3 -u main.py          \
  --serial_number ${SERIAL_NUMBER}     \
  --dynamodb_activation_table ${DYNAMODB_ACTIVATION_TABLE}   \
  --dynamodb_metrics_storage_table ${DYNAMODB_METRICS_STORAGE_TABLE}   \
  --dynamodb_region ${DYNAMODB_REGION} \
  --s3_bucket ${S3_BUCKET} \
  --s3_dir ${S3_DIR}       \
  --region ${REGION}
