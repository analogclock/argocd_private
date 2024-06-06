# Upload image to ECR

Ensure your AWS CLI is configured and the user has permission to upload to ECR.
Build the image with docker-compose:

```bash
sudo docker-compose build fsiem-deploy
```

Prepare and upload the image to the dev ECR repository (or other as required):

```bash
aws ecr get-login-password --region us-east-1 | sudo docker login --username AWS --password-stdin 023941436530.dkr.ecr.us-east-1.amazonaws.com
sudo docker tag fsiem-deploy:latest 023941436530.dkr.ecr.us-east-1.amazonaws.com/fsiem-deploy-dev:latest
sudo docker push 023941436530.dkr.ecr.us-east-1.amazonaws.com/fsiem-deploy-dev:latest
```

## Plan playground deployment from a local machine

This helps if you want to test if your terraform can be successfully planned.

### Define a playground profile in your AWS cred file

```sh
cat <<EOF >> ~/.aws/credentials

[playground]
aws_access_key_id=<get_from_lastpass>
aws_secret_access_key=<get_from_lastpass>
EOF
```

### Make a folder and HCL file in it

```sh
mkdir -p src/terraform/fsiem_deploy/FSMCLD0000000154
cd  src/terraform/fsiem_deploy/FSMCLD0000000154

cat <<EOF > terragrunt.hcl
include { path = find_in_parent_folders() }
remote_state {
  backend = "s3"
  generate = { path = "backend.tf", if_exists = "overwrite_terragrunt" }
  config = {
    bucket = "fsiem-terraform-ftn"
    key = "portal/\${path_relative_to_include()}/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
  }
}
inputs = {
    region = "us-east-1"
    environment = "playground"
    serial_number = "FSMCLD0000000154"
    deployment_email = "omandrychenko@fortinet.com"
    storage_type = "clickhouse"
    customer_cidrs = "0.0.0.0/0"
    customer_cidrs_ipv6 = "::/0"
}
terraform { source = "..//ec2//" }
EOF
```

### Plan deployment with exported AWS env

This one-liner won't mess up your other deployments, because the exported `AWS_PROFILE`

```sh
export AWS_PROFILE=playground; \
terragrunt plan
```

### **Danger zone**. You can run a test deployment and destruction. You should only do this

if you are using the `playground` and the environment is otherwise busy. The advised method
is via UI portal deployment.

Some things will not work - it's not a proper deployment, e.g. saving a password
in a secrets manager. You have been warned. But if you know what ya do:

```sh
# Insert an entry for the stack, this is what API does
AWS_PROFILE=playground
PORTAL_AWS_REGION="us-east-1"
DEPLOYMENT_NAME="FSMCLD0000000154"
DYNAMODB_ACTIVATION_TABLE="fsiem_activation_table_playground"
CMD="INSERT INTO $DYNAMODB_ACTIVATION_TABLE VALUE {'serialNumber':'$DEPLOYMENT_NAME'}"
aws dynamodb execute-statement --region us-east-1 --statement "$CMD"

# Deploy
export AWS_PROFILE DEPLOYMENT_NAME PORTAL_AWS_REGION DYNAMODB_ACTIVATION_TABLE; \
terragrunt apply

# Delete
export AWS_PROFILE DEPLOYMENT_NAME PORTAL_AWS_REGION DYNAMODB_ACTIVATION_TABLE; \
terragrunt destroy
```
