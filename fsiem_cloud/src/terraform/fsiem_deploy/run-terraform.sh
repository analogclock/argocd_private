#!/bin/bash -e

# Pass these via env variables, or use defaults
action=${DEPLOYMENT_ACTION:-"apply"}
aws_region=${AWS_REGION:-"us-east-1"}
environment=${ENVIRONMENT:-"dev"}
workload_classification=${WORKLOAD_CLASSIFICATION:-"dev"}
deployment_bucket=${DEPLOYMENT_BUCKET:-"fsiem-terraform"}
deployment_bucket_region=${DEPLOYMENT_BUCKET_REGION:-"us-east-1"}
deployment_name=${DEPLOYMENT_NAME:-"new_deployment"}
deployment_type=${DEPLOYMENT_TYPE:-"va"}
deployment_email=${DEPLOYMENT_EMAIL:-"test@test.com"}
dynamodb_compute_override_table=${DYNAMODB_COMPUTE_OVERRIDE_TABLE:-"fsiem_compute_override_dev"}
updating_deployment=${UPDATING_DEPLOYMENT:-"false"}
ipv4_cidrs=${IPV4_CIDRS:-"0.0.0.0/0"}
ipv6_cidrs=${IPV6_CIDRS:-"::/0"}
compute_size=${COMPUTE_SIZE:-"5"}
live_storage_size=${LIVE_STORAGE:-"1"}
archive_storage_size=${ARCHIVE_STORAGE:-"1"}
is_poc=${IS_POC:-"false"}
alternate_domain_certificate_arn=${ALTERNATE_DOMAIN_CERTIFICATE_ARN:-""}
primary_az=${PRIMARY_AZ:-""}
external_storage_dest=${EXTERNAL_STORAGE_DEST:-""}

online_storage_gb="500"
# add 50 GB buffer, so that 100 GB disk for smaller deployments become a 110 GB disk
# this avoids a conflict during FSIEM setup when we assigning disks for OPT volume
total_online_size=$(($live_storage_size*$online_storage_gb + 50))
max_disk_size=${MAX_DISK_SIZE:-"12050"}

echo "Create new deployment at $(date +"%F:%T")"

# Get compute override values from overrides dynamodb table
echo "Retrieving compute overrides"
db_cmd="SELECT * FROM $dynamodb_compute_override_table WHERE serialNumber='$deployment_name'"
aws dynamodb execute-statement --region "$deployment_bucket_region" --statement "$db_cmd" --output json | \
  jq --raw-output '.Items[]' | jq -f parse-dynamodb-output.jq > fsiem_resource_override.json

if [ -s fsiem_resource_override.json ]; then
  # Check fsiem_resource_config.json for compute size
  # If set then override $compute_size ahead of fsiem_resource_calc
  value=$(jq -r ".compute_override" "fsiem_resource_override.json")
  if [ "$value" != "null" ]; then
  echo "Overriding compute from $compute_size to $value"
    compute_size="$value"
  fi
fi

echo "Make clickhouse deployment config for $compute_size seats"
./bin/fsiem_resource_calc -s $compute_size -t 'clickhouse' -o $total_online_size -m $max_disk_size > fsiem_resource_config.json
echo "Generated config:"
cat fsiem_resource_config.json

while read -r key ; do
    read -r value

    # If fsiem_resource_override is not empty then overrides were found in the table.
    # Check each resource type exists in fsiem_resource_override, if so override the value
    # from fsiem_resource_config
    if [ -s fsiem_resource_override.json ]
    then
      value=$(jq -c --raw-output \
        --arg type "$value" \
        --arg keyname "$key" \
        'if .[$keyname]? then .[$keyname] else $type end' fsiem_resource_override.json)
    fi

    export "$key"="$value"
done < <(< fsiem_resource_config.json jq -c -r '. | to_entries[] | .key, .value')

echo "Action:                   '$action'"
echo "AWS Region:               '$aws_region'"
echo "Environment:              '$environment'"
echo "Workload classification:  '$workload_classification'"
echo "Deployment bucket:        '$deployment_bucket'"
echo "Deployment bucket region: '$deployment_bucket_region'"
echo "Deployment name:          '$deployment_name'"
echo "Deployment type:          '$deployment_type'"
echo "Deployment email:         '$deployment_email'"
echo "Updating deployment?      '$updating_deployment'"
echo "Is POC deployment?        '$is_poc'"
echo "IPV4 cidrs:               '$ipv4_cidrs'"
echo "IPV6 cidrs:               '$ipv6_cidrs'"
echo "Compute Size:             '$compute_size'"
echo "Live Storage Size:        '$live_storage_size'"
echo "Archive Storage Size:     '$archive_storage_size'"
echo "Alternate Certificate     '$alternate_domain_certificate_arn'"
echo "Primary AZ:               '$primary_az'"
echo "External Storage Dest:    '$external_storage_dest'"

# Calculated and exported by fsiem_resource_calc above
echo "shards:                   '$shards'"
echo "replicas:                 '$replicas'"
echo "data_workers:             '$data_workers'"
echo "keeper_workers:           '$keeper_workers'"
echo "ingestion_workers:        '$ingestion_workers'"
echo "super_instance_types:     '$super_instance_types'"
echo "worker_instance_types:    '$worker_instance_types'"
echo "ingestion_instance_types: '$ingestion_instance_types'"
echo "keeper_instance_types:    '$keeper_instance_types'"
echo "cmdb_iops:                '$cmdb_iops'"
echo "cmdb_throughput:          '$cmdb_throughput'"
echo "opt_iops:                 '$opt_iops'"
echo "opt_throughput:           '$opt_throughput'"
echo "data_disk_throughput:     '$data_disk_throughput'"
echo "data_disk_iops:           '$data_disk_iops'"
echo "data_disk_count:          '$data_disk_count'"
echo "data_disk_size:           '$data_disk_size'"
echo "app_server_mem_gb:        '$app_server_mem_gb'"

echo "Create terragrunt deployment folder $deployment_name"
mkdir -p $deployment_name
cd $deployment_name

# Create default terragrunt file
# TODO: Shall we control this from outside?
echo "Create new terragrunt .hcl specification"
cat <<EOF >terragrunt.hcl
include {
  # this will pick out the first .hcl file in the parent root dir
  # so that we don't need to recreate hooks to track deployment progress
  path = find_in_parent_folders()
}
remote_state {
  backend = "s3"
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
  config = {
    bucket = "$deployment_bucket"
    key = "portal/$environment/$deployment_name/terraform.tfstate"
    region         = "$deployment_bucket_region"
    dynamodb_table = "tf_state_lock_$environment"
    encrypt        = true
  }
}
inputs = {
    region                           = "$aws_region"
    environment                      = "$environment"
    workload_classification          = "$workload_classification"
    serial_number                    = "$deployment_name"
    deployment_email                 = "$deployment_email"
    customer_cidrs                   = "$ipv4_cidrs"
    customer_cidrs_ipv6              = "$ipv6_cidrs"
    deployment_type                  = "$deployment_type"
    compute_size                     = $compute_size
    live_storage                     = $live_storage_size
    archive_storage                  = $archive_storage_size
    is_poc                           = $is_poc
    alternate_domain_certificate_arn = "$alternate_domain_certificate_arn"
    primary_az                       = "$primary_az"
    external_storage_dest            = "$external_storage_dest"

    # These vars are calculated by fsiem_resource_calc
    shards                   = $shards
    replicas                 = $replicas
    data_workers             = $data_workers
    keeper_workers           = $keeper_workers
    ingestion_workers        = $ingestion_workers
    super_instance_types     = $super_instance_types
    worker_instance_types    = $worker_instance_types
    keeper_instance_types    = $keeper_instance_types
    ingestion_instance_types = $ingestion_instance_types
    cmdb_iops                = $cmdb_iops
    cmdb_throughput          = $cmdb_throughput
    opt_iops                 = $opt_iops
    opt_throughput           = $opt_throughput
    data_disk_throughput     = $data_disk_throughput
    data_disk_iops           = $data_disk_iops
    data_disk_count          = $data_disk_count
    data_disk_size           = $data_disk_size
    app_server_mem_gb        = $app_server_mem_gb
}
terraform {
    # it needs 4 slashes for tf linter
    source = "..////ec2////"
}
EOF

# Deploy
echo "Run terragrunt $action..."
# Update internal variable
export TF_VAR_instance_name="$deployment_name"
export TF_VAR_region="$aws_region"
export UPDATING_DEPLOYMENT="$updating_deployment"

# allows for upgraded terraform modules
terragrunt init -upgrade -no-color -migrate-state

# -auto-approve: automatically applies changes without asking for user confirmation
# -compact-warnings: makes reading of the log easier in CloudWatch
terragrunt $action -auto-approve -compact-warnings -no-color

echo "$action finished on $(date +"%F:%T")"
