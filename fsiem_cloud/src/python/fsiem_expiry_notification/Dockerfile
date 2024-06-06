ARG DOCKER_REGISTRY=""
ARG DOCKER_PYTHON_VERSION
FROM ${DOCKER_REGISTRY}python:${DOCKER_PYTHON_VERSION}

ARG NEXUS_PYPI_URL

WORKDIR /app/fsiem_expiry_notification
COPY ./fsiem_expiry_notification .
COPY ./fsiem_api_client /app/fsiem_api_client

ENV DYNAMODB_ACTIVATION_TABLE=""
ENV EMAIL_BLOCK_TABLE=""
ENV DYNAMODB_REGION=""
ENV FROM_ADDRESS=""
ENV FSIEM_BCC_ADDRESS=""
ENV PORTAL_DOMAIN=""

RUN set -eux && \
  pip3 install -r requirements.txt --quiet --no-cache-dir --no-build-isolation --root-user-action ignore --index-url ${NEXUS_PYPI_URL} && \
  pip3 install -r requirements-unittest.txt --quiet --no-cache-dir --no-build-isolation --root-user-action ignore --index-url ${NEXUS_PYPI_URL} && \
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

ENTRYPOINT python3 -u main.py --activation_table ${DYNAMODB_ACTIVATION_TABLE} --email_block_table ${EMAIL_BLOCK_TABLE} \
  --dynamodb_region ${DYNAMODB_REGION} --from_address ${FROM_ADDRESS} --fsiem_address ${FSIEM_BCC_ADDRESS} \
  --portal_domain ${PORTAL_DOMAIN}
