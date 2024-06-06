ARG DOCKER_REGISTRY=""
ARG DOCKER_PYTHON_VERSION
FROM ${DOCKER_REGISTRY}python:${DOCKER_PYTHON_VERSION}

ARG NEXUS_PYPI_URL

WORKDIR /app/fsiem_backup
COPY ./fsiem_backup .
COPY ./fsiem_api_client /app/fsiem_api_client

# Tell python to flush output stream w/o buffering, helps with sending a few
# printouts for long-running process promptly
ENV PYTHONUNBUFFERED=TRUE

# Email notification settings
ENV EMAIL_FROM_ADDR=""
ENV EMAIL_TO_ADDR=""

ENV SERIAL_NUMBER=""
ENV DYNAMODB_REGION=""
ENV DYNAMODB_BACKUP_TABLE=""
ENV DYNAMODB_BACKUP_OPTIONS_TABLE=""
ENV DYNAMODB_ACTIVATION_TABLE=""
ENV REGION=""

# Backup variables
ENV REMOTE_STORAGE="s3"
ENV LOG_LEVEL="warn"
# E.g. S3_BUCKET="fsiem-clickhouse-backups-us-east-1-playground"
ENV S3_BUCKET=""
# E.g. S3_PATH="FSMCLD0000000154"
ENV S3_PATH=""
ENV S3_COMPRESSION_LEVEL="1"
ENV S3_COMPRESSION_FORMAT="tar"
ENV S3_USE_CUSTOM_STORAGE_CLASS="false"
ENV S3_STORAGE_CLASS="STANDARD"
ENV S3_CONCURRENCY="1"
ENV S3_DEBUG="false"

ENV MAX_BACKUPS_IN_CHAIN="3"

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

ENTRYPOINT python3 main.py --serial_number ${SERIAL_NUMBER} \
  --dynamodb_region ${DYNAMODB_REGION} \
  --dynamodb_activation_table ${DYNAMODB_ACTIVATION_TABLE} \
  --dynamodb_backup_table ${DYNAMODB_BACKUP_TABLE} \
  --dynamodb_backup_options_table ${DYNAMODB_BACKUP_OPTIONS_TABLE} \
  --remote_storage ${REMOTE_STORAGE} --log_level ${LOG_LEVEL} \
  --s3_bucket ${S3_BUCKET} --region ${REGION}\
  --s3_path ${S3_PATH} --s3_compression_level ${S3_COMPRESSION_LEVEL} \
  --s3_compression_format ${S3_COMPRESSION_FORMAT} \
  --s3_use_custom_storage_class ${S3_USE_CUSTOM_STORAGE_CLASS} \
  --s3_storage_class ${S3_STORAGE_CLASS} --s3_concurrency ${S3_CONCURRENCY} \
  --s3_debug ${S3_DEBUG} \
  --max_backups_in_chain ${MAX_BACKUPS_IN_CHAIN} \
  --email_from_addr ${EMAIL_FROM_ADDR} --email_to_addr ${EMAIL_TO_ADDR}
