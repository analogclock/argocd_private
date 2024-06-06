ARG DOCKER_REGISTRY=""
ARG DOCKER_PYTHON_VERSION
FROM ${DOCKER_REGISTRY}python:${DOCKER_PYTHON_VERSION}

ARG NEXUS_PYPI_URL

WORKDIR /app/fsiem_worker_lifecycle
COPY ./fsiem_worker_lifecycle .
COPY ./fsiem_api_client /app/fsiem_api_client

ENV SQS_QUEUE_NAME=""
ENV SUPER_ADDRESS=""
ENV SECRET_VM_AUTH=""
ENV COGNITO_URL=""
ENV SERIAL_NO=""
ENV ENVIRONMENT=""
ENV CLUSTER_REGION=""
ENV PORTAL_REGION=""
ENV S3_BUCKET=""
ENV S3_REGION=""
ENV DYNAMODB_ACTIVATION_TABLE=""
ENV SETUP_DOC_NAME=""
ENV AUTOMATION_ROLE_NAME=""
ENV FMON_CUST_KEY=""

RUN set -eux && \
  pip3 install -r requirements.txt --index-url ${NEXUS_PYPI_URL} --quiet

ENTRYPOINT python3 -u main.py --queue_name ${SQS_QUEUE_NAME} \
  --super_address ${SUPER_ADDRESS} --secret_vm_auth ${SECRET_VM_AUTH} \
  --cognito_url ${COGNITO_URL} --serial_no ${SERIAL_NO} --environment ${ENVIRONMENT} \
  --cluster_region ${CLUSTER_REGION} --portal_region ${PORTAL_REGION} --s3_bucket ${S3_BUCKET} \
  --s3_region ${S3_REGION} --activation_table ${DYNAMODB_ACTIVATION_TABLE} \
  --setup_doc_name ${SETUP_DOC_NAME} --automation_role_name ${AUTOMATION_ROLE_NAME} \
  --fmon_cust_key ${FMON_CUST_KEY}
