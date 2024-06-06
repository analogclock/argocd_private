ARG DOCKER_REGISTRY=""
ARG DOCKER_PYTHON_VERSION
FROM ${DOCKER_REGISTRY}python:${DOCKER_PYTHON_VERSION}

ARG NEXUS_PYPI_URL

WORKDIR /app/fsiem_setup
COPY ./fsiem_setup .
COPY ./fsiem_api_client /app/fsiem_api_client

ENV SUPER_URL=""
ENV CLICKHOUSE_S3_BUCKET=""
ENV CLICKHOUSE_S3_REGION=""
ENV SECRET_ID_VM_AUTH=""
ENV COGNITO_URL=""
ENV NEW_PASSWORD=""
ENV WORKER_URL=""
ENV EMAIL="test@test.com"
ENV SERIAL_NUMBER=""
ENV DYNAMODB_ACTIVATION_TABLE=""
ENV DYNAMODB_REGION=""
ENV APP_SERVER_MEM_GB=""

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
  pip3 uninstall -y setuptools coverage pip >/dev/null && \
  rm -rf /root/.cache/pip && \
  find / | grep -E "(/__pycache__$|\.pyc$|\.pyo|\.exe$)" | xargs rm -rf && \
  BOTO_DATA=/usr/local/lib/python3.11/site-packages/botocore/data && \
  find $BOTO_DATA | grep examples-1.json | xargs rm -rf && \
  find $BOTO_DATA/ec2 -mindepth 1 -type d | sort -r | tail -n +2 | xargs rm -rf && \
  find $BOTO_DATA/cloudfront -mindepth 1 -type d | sort -r | tail -n +2 | xargs rm -rf && \
  rm -rf $BOTO_DATA/sagemaker $BOTO_DATA/rds $BOTO_DATA/mediaconvert

ENTRYPOINT python3 -u main.py --super ${SUPER_URL} \
  --secret_vm_auth ${SECRET_VM_AUTH} --cognito_url ${COGNITO_URL} \
  --clickhouse_s3_bucket ${CLICKHOUSE_S3_BUCKET} \
  --clickhouse_s3_region ${CLICKHOUSE_S3_REGION} \
  --new_password ${NEW_PASSWORD} \
  --worker_url ${WORKER_URL} --email ${EMAIL} \
  --serial_number ${SERIAL_NUMBER} --dynamodb_table ${DYNAMODB_ACTIVATION_TABLE} \
  --dynamodb_region ${DYNAMODB_REGION} --app_server_mem_gb ${APP_SERVER_MEM_GB}
