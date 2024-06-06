/*
  This is the ec2 instances for keepers
*/
data "aws_subnet" "keeper" {
  id = module.vpc.private_subnets[0]
}

data "aws_ec2_instance_type_offering" "keeper" {
  count = var.keeper_workers
  filter {
    name   = "instance-type"
    values = var.keeper_instance_types
  }
  filter {
    name   = "location"
    values = [data.aws_subnet.keeper.availability_zone_id]
  }
  location_type            = "availability-zone-id"
  preferred_instance_types = var.keeper_instance_types
}

resource "aws_instance" "keeper" {
  count = var.keeper_workers
  ami   = local.siem_ami
  root_block_device {
    encrypted   = true
    volume_size = 25
    volume_type = "gp3"
    tags = merge(
      local.global_tags,
      {
        Name   = "${var.serial_number}_keeper_${count.index}_root"
        Backup = var.environment
      }
    )
  }

  iam_instance_profile   = aws_iam_instance_profile.instance_profile.id
  instance_type          = data.aws_ec2_instance_type_offering.keeper[count.index].id
  subnet_id              = data.aws_subnet.keeper.id
  vpc_security_group_ids = [aws_security_group.keeper[0].id]
  user_data = templatefile(
    "install_siem_worker.sh",
    {
      user                     = "ec2-user"
      env                      = var.environment
      id                       = jsondecode(data.aws_secretsmanager_secret_version.fortimonitor.secret_string)["customer_key"]
      serial_no                = var.serial_number
      s3_scripts_bucket        = local.s3_scripts_bucket
      s3_scripts_bucket_region = local.portal_region
      num_exp_disks            = 3 # for keeper (1 root, 1 clickhouse, 1 opt)
      fmon_server_key          = "${var.serial_number}_${var.environment}_agent_keeper_${count.index}"
    }
  )
  tags = {
    Name = "${var.serial_number}_keeper_${count.index}"
    Role = "keeper"
  }
  lifecycle {
    # This stops the instance from being deleted and recreated if any of these change, including all data
    ignore_changes = [user_data, ami]
  }
}
# AWS docs suggest /dev/sd[f-p] names for EBS volumes
# opt ebs volume for keeper instances
resource "aws_volume_attachment" "ebs_keeper_opt_vol_att" {
  count                          = var.keeper_workers
  device_name                    = "/dev/sdf"
  volume_id                      = aws_ebs_volume.ebs_keeper_opt_volume[count.index].id
  instance_id                    = aws_instance.keeper[count.index].id
  stop_instance_before_detaching = true
}

resource "aws_ebs_volume" "ebs_keeper_opt_volume" {
  count             = var.keeper_workers
  availability_zone = data.aws_subnet.keeper.availability_zone
  encrypted         = true
  size              = 100
  type              = "gp3"
  iops              = var.opt_iops
  throughput        = var.opt_throughput
  tags = {
    Name   = "${var.serial_number}_keeper_${count.index}_opt"
    Backup = var.environment
  }
}

# keeper data ebs volume for keeper instances
resource "aws_volume_attachment" "ebs_keeper_keeper_data_vol_att" {
  count                          = var.keeper_workers
  device_name                    = "/dev/sdg"
  volume_id                      = aws_ebs_volume.ebs_keeper_data_volume[count.index].id
  instance_id                    = aws_instance.keeper[count.index].id
  stop_instance_before_detaching = true
}

resource "aws_ebs_volume" "ebs_keeper_data_volume" {
  count             = var.keeper_workers
  availability_zone = data.aws_subnet.keeper.availability_zone
  encrypted         = true
  size              = local.keeper_disk_size
  type              = "gp3"
  tags = {
    Name = "${var.serial_number}_keeper_${count.index}_data"
  }
}
