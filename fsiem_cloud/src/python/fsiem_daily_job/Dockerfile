ARG DOCKER_REGISTRY=""
ARG DOCKER_PYTHON_VERSION
FROM ${DOCKER_REGISTRY}python:${DOCKER_PYTHON_VERSION}

ARG NEXUS_PYPI_URL

WORKDIR /app/fsiem_daily_job
COPY ./fsiem_daily_job .
COPY ./fsiem_api_client /app/fsiem_api_client

# Tell python to flush output stream w/o buffering, helps with sending a few
# printouts for long-running process promptly
ENV PYTHONUNBUFFERED=TRUE

ENV AWS_ACCOUNT_ID=""
ENV DYNAMODB_REGION=""
ENV DYNAMODB_ACTIVATION_TABLE=""
ENV LAMBDA_REGION=""
ENV S3_TAG_LAMBDA_NAME=""
ENV S3_TAG_LAMBDA_ROLE_ARN=""
ENV S3_MANIFEST_BUCKET=""
ENV ENVIRONMENT=""
ENV EMAIL_FROM_ADDR=""
ENV EMAIL_TO_ADDR=""

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

ENTRYPOINT python3 main.py \
  --aws_account_id ${AWS_ACCOUNT_ID} \
  --dynamodb_region ${DYNAMODB_REGION} \
  --dynamodb_activation_table ${DYNAMODB_ACTIVATION_TABLE} \
  --lambda_region ${LAMBDA_REGION} \
  --s3_tag_lambda_name ${S3_TAG_LAMBDA_NAME} \
  --s3_tag_lambda_role_arn ${S3_TAG_LAMBDA_ROLE_ARN} \
  --s3_manifest_bucket ${S3_MANIFEST_BUCKET} \
  --environment ${ENVIRONMENT} \
  --email_from_addr ${EMAIL_FROM_ADDR} \
  --email_to_addr ${EMAIL_TO_ADDR}
