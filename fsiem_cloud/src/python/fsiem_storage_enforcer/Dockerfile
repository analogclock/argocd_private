ARG DOCKER_REGISTRY=""
ARG DOCKER_PYTHON_VERSION
FROM ${DOCKER_REGISTRY}python:${DOCKER_PYTHON_VERSION}

ARG NEXUS_PYPI_URL

WORKDIR /app/fsiem_storage_enforcer
COPY ./fsiem_storage_enforcer .
COPY ./fsiem_api_client /app/fsiem_api_client

ENV SN=""
ENV REGION=""
ENV SIZE_LIMIT_GB=100
ENV BUFFER_GB=20
ENV DYNAMODB_EXT_STORAGE_TABLE=""
ENV DYNAMODB_EXT_STORAGE_STATUS_TABLE=""
ENV DYNAMODB_REGION=""

RUN set -eux && \
  pip3 install -r requirements.txt --index-url ${NEXUS_PYPI_URL} --quiet && \
  pip3 install -r requirements-unittest.txt --index-url ${NEXUS_PYPI_URL} --quiet && \
  ./build/unittest.sh && \
  # This image is manually minimized for runtime use
  # Using ncdu and dive tools, the following are deleted:
  # - Largest python packages not required for runtime
  # - Pip and pip cache files
  # - Boto: example files
  # - Boto: only latest version kept for ec2 and cloudfront json files
  # - Boto: removed largest and non used components: sagemaker, rds, mediaconvert
  pip3 uninstall -y --quiet -r requirements-unittest.txt && \
  pip3 uninstall -y setuptools coverage pip > /dev/null && \
  rm -rf /root/.cache/pip && \
  find / | grep -E "(/__pycache__$|\.pyc$|\.pyo|\.exe$)" | xargs rm -rf && \
  BOTO_DATA=/usr/local/lib/python3.11/site-packages/botocore/data && \
  find $BOTO_DATA | grep examples-1.json | xargs rm -rf && \
  find $BOTO_DATA/ec2        -mindepth 1 -type d | sort -r | tail -n +2 | xargs rm -rf && \
  find $BOTO_DATA/cloudfront -mindepth 1 -type d | sort -r | tail -n +2 | xargs rm -rf && \
  rm -rf $BOTO_DATA/sagemaker $BOTO_DATA/rds $BOTO_DATA/mediaconvert

ENTRYPOINT python3 -u main.py      \
  --sn "${SN}"                     \
  --region "${REGION}"             \
  --size_limit_gb ${SIZE_LIMIT_GB} \
  --buffer_gb ${BUFFER_GB}         \
  --dynamodb_ext_st_table ${DYNAMODB_EXT_STORAGE_TABLE}   \
  --dynamodb_region ${DYNAMODB_REGION} \
  --dynamodb_ext_st_status_table ${DYNAMODB_EXT_STORAGE_STATUS_TABLE}
