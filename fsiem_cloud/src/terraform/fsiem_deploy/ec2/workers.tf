/*
  This is the ec2 instance for the workers
*/
data "aws_subnet" "worker" {
  id = module.vpc.private_subnets[0]
}

data "aws_ec2_instance_type_offering" "worker" {
  count = var.data_workers
  filter {
    name   = "instance-type"
    values = var.worker_instance_types
  }
  filter {
    name   = "location"
    values = [data.aws_subnet.worker.availability_zone_id]
  }
  location_type            = "availability-zone-id"
  preferred_instance_types = var.worker_instance_types
}

resource "aws_instance" "worker" {
  count = var.data_workers
  ami   = local.siem_ami
  root_block_device {
    encrypted   = true
    volume_size = 25
    volume_type = "gp3"
    tags = merge(
      local.global_tags,
      {
        Name   = "${var.serial_number}_worker_${count.index}_root"
        Backup = var.environment
      }
    )
  }

  iam_instance_profile   = aws_iam_instance_profile.instance_profile.id
  instance_type          = data.aws_ec2_instance_type_offering.worker[count.index].id
  subnet_id              = data.aws_subnet.worker.id
  vpc_security_group_ids = [aws_security_group.worker.id]
  user_data = templatefile(
    "install_siem_worker.sh",
    {
      user                     = "ec2-user"
      env                      = var.environment
      id                       = jsondecode(data.aws_secretsmanager_secret_version.fortimonitor.secret_string)["customer_key"]
      serial_no                = var.serial_number
      s3_scripts_bucket        = local.s3_scripts_bucket
      s3_scripts_bucket_region = local.portal_region
      num_exp_disks            = 7 # for worker (1 root, 5 clickhouse, 1 opt)
      fmon_server_key          = "${var.serial_number}_${var.environment}_agent_worker_${count.index}"
    }
  )
  tags = {
    Name = "${var.serial_number}_worker_${count.index}"
    Role = "worker"
  }
  lifecycle {
    # This stops the instance from being deleted and recreated if any of these change, including all data
    ignore_changes = [user_data, ami]
  }
}
# AWS docs suggest /dev/sd[f-p] names for EBS volumes
# opt ebs volume for worker instances
resource "aws_volume_attachment" "ebs_worker_opt_vol_att" {
  count                          = var.data_workers
  device_name                    = "/dev/sdf"
  volume_id                      = aws_ebs_volume.ebs_worker_opt_volume[count.index].id
  instance_id                    = aws_instance.worker[count.index].id
  stop_instance_before_detaching = true
}

resource "aws_ebs_volume" "ebs_worker_opt_volume" {
  count             = var.data_workers
  availability_zone = data.aws_subnet.worker.availability_zone
  encrypted         = true
  size              = 100
  type              = "gp3"
  iops              = var.opt_iops
  throughput        = var.opt_throughput
  tags = {
    Name   = "${var.serial_number}_worker_${count.index}_opt"
    Backup = var.environment
  }
  # add additional timeout
  timeouts {
    create = local.create_timeout
    update = local.update_timeout
    delete = local.delete_timeout
  }
}

# add as many disks as we require
# this will add to each worker, and also attach
module "clickhouse_data_attachment" {
  count  = var.data_workers
  source = "./modules/clickhouse_online_storage/"

  number_of_data_volumes        = var.data_disk_count
  data_disk_name_prefix         = "${var.serial_number}_worker_${count.index}_clickhouse"
  data_worker_volume_iops       = var.data_disk_iops
  data_worker_volume_throughput = var.data_disk_throughput
  data_worker_volume_size_gb    = var.data_disk_size
  disk_create_timeout           = local.create_timeout
  disk_delete_timeout           = local.delete_timeout
  disk_update_timeout           = local.update_timeout
  worker_availability_zone      = data.aws_subnet.worker.availability_zone
  worker_instance_id            = aws_instance.worker[count.index].id
}
