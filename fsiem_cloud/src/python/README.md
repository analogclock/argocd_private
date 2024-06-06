# Build

```bash
# Change dir to python folder
cd ~/git/fsiem_saas/src/python

# Set the variables which will be used for build/tag/push
IMG_NAME=fsiem-metrics
ENV=playground
AWS_REGION=us-east-1
AWS_ACCOUNT=023941436530
ACCOUNT=$AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com

# To build all python docker images
sudo docker-compose build

# To build a specific python docker image
# For a list of available images see src/python/docker-compose.yml
sudo docker-compose build $IMG_NAME
```

## Tag and push the image

```bash
aws ecr get-login-password --region $AWS_REGION | sudo docker login --username AWS --password-stdin $ACCOUNT
export CONTAINER_IMAGE_NAME="$ACCOUNT/$IMG_NAME-$ENV:latest"
sudo docker-compose build --progress=plain "$IMG_NAME"
sudo docker-compose push "$IMG_NAME"
```

## Testing

Most projects have unit tests, that run during CI build. Some projects have
integration tests which require some configuration and local changes. Integration tests
do not run on CI, but can be run locally via a script or from VS Code
(install VS Code `littlefoxteam.vscode-python-test-adapter` extension).

```bash
cd src/python/<project_name>

# unit tests
sh build/unittest.sh
# view coverage report after unit test script finished
open htmlcov/index.html
# integration tests
sh build/integrationtest.sh
```

If you get an error:

> import file mismatch:
> imported module 'test_ssm' has this __file__ attribute:
>   /home/om/git/fsiem_saas/src/python/fsiem_api_client/integration-tests/aws/test_ssm.py
> which is not the same as the test file we want to collect:
>   /home/om/git/fsiem_saas/src/python/fsiem_api_client/tests/aws/test_ssm.py
> HINT: remove __pycache__ / .pyc files and/or use a unique basename for your test file modules

Run
```bash
cd src/python
find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf
```
