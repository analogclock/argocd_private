ARG DOCKER_REGISTRY=""
ARG DOCKER_PYTHON_VERSION
FROM ${DOCKER_REGISTRY}python:${DOCKER_PYTHON_VERSION}

ARG NEXUS_PYPI_URL

WORKDIR /app/fsiem_license
COPY ./fsiem_license .
COPY ./fsiem_api_client /app/fsiem_api_client

ENV SUPER_URL=""
ENV LICENSE_TYPE=""
ENV DEFAULT_PASSWORD=""
ENV NEW_PASSWORD=""
ENV SECRET_ID=""
ENV COGNITO_URL=""
ENV PORTAL_API_URL=""
ENV SERIAL_NUMBER=""
ENV DYNAMODB_ACTIVATION_TABLE=""
ENV DYNAMODB_REGION=""
ENV SECRET_ID_VM_AUTH=""


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

ENTRYPOINT python3 main.py --super ${SUPER_URL} --license_type ${LICENSE_TYPE} \
  --default_password ${DEFAULT_PASSWORD} --new_password ${NEW_PASSWORD}  \
  --secret_vm_auth ${SECRET_ID_VM_AUTH} --secret_id ${SECRET_ID} \
  --cognito_url ${COGNITO_URL} --portal_api_url ${PORTAL_API_URL} --serial_number ${SERIAL_NUMBER} \
  --dynamodb_table ${DYNAMODB_ACTIVATION_TABLE} --dynamodb_region ${DYNAMODB_REGION}
