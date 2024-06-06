/*
  This is the ec2 instance for the FSIEM supervisor node
*/
data "aws_subnet" "super" {
  id = module.vpc.private_subnets[0]
}

data "aws_ec2_instance_type_offering" "super" {
  filter {
    name   = "instance-type"
    values = var.super_instance_types
  }
  filter {
    name   = "location"
    values = [data.aws_subnet.super.availability_zone_id]
  }
  location_type            = "availability-zone-id"
  preferred_instance_types = var.super_instance_types
}

resource "aws_instance" "super" {
  ami = local.siem_ami
  root_block_device {
    encrypted   = true
    volume_size = 25
    volume_type = "gp3"
    tags = merge(
      local.global_tags,
      {
        Name   = "${var.serial_number}_super_root"
        Backup = var.environment
      }
    )
  }

  iam_instance_profile   = aws_iam_instance_profile.instance_profile.id
  instance_type          = data.aws_ec2_instance_type_offering.super.id
  subnet_id              = data.aws_subnet.super.id
  vpc_security_group_ids = [aws_security_group.super.id]
  user_data = templatefile(
    "install_siem_super.sh",
    {
      user                     = "ec2-user"
      env                      = var.environment
      id                       = jsondecode(data.aws_secretsmanager_secret_version.fortimonitor.secret_string)["customer_key"]
      serial_no                = var.serial_number
      s3_scripts_bucket        = local.s3_scripts_bucket
      s3_scripts_bucket_region = local.portal_region
      host_input               = "${aws_route53_record.super.fqdn}"
      num_exp_disks            = 5 # for super (1 root, 1 cmdb, 1 opt, 1 svn, 1 clickhouse)
      fmon_server_key          = "${var.serial_number}_${var.environment}_agent_super"
    }
  )
  tags = {
    Name = "${var.serial_number}_super"
    Role = "super"
  }
  lifecycle {
    # This stops the instance from being deleted and recreated if any of these change, including all data
    ignore_changes = [user_data, ami]
  }
}
# AWS docs suggest /dev/sd[f-p] names for EBS volumes
# opt ebs volume for super instance
resource "aws_volume_attachment" "ebs_super_opt_vol_att" {
  device_name                    = "/dev/sdf"
  volume_id                      = aws_ebs_volume.ebs_super_opt_volume.id
  instance_id                    = aws_instance.super.id
  stop_instance_before_detaching = true
}

resource "aws_ebs_volume" "ebs_super_opt_volume" {
  availability_zone = data.aws_subnet.super.availability_zone
  encrypted         = true
  size              = 100
  type              = "gp3"
  iops              = var.opt_iops
  throughput        = var.opt_throughput
  tags = {
    Name   = "${var.serial_number}_super_opt"
    Backup = var.environment
  }
  # add additional timeout
  timeouts {
    create = local.create_timeout
    update = local.update_timeout
    delete = local.delete_timeout
  }
}
# cmdb ebs volume for super instance
resource "aws_volume_attachment" "ebs_super_cmdb_vol_att" {
  device_name                    = "/dev/sdg"
  volume_id                      = aws_ebs_volume.ebs_super_cmdb_volume.id
  instance_id                    = aws_instance.super.id
  stop_instance_before_detaching = true
}
resource "aws_ebs_volume" "ebs_super_cmdb_volume" {
  availability_zone = data.aws_subnet.super.availability_zone
  encrypted         = true
  size              = 80
  type              = "gp3"
  iops              = var.cmdb_iops
  throughput        = var.cmdb_throughput
  tags = {
    Name   = "${var.serial_number}_super_cmdb"
    Backup = var.environment
  }
  # add additional timeout
  timeouts {
    create = local.create_timeout
    update = local.update_timeout
    delete = local.delete_timeout
  }
}
# svn ebs volume for super instance
resource "aws_volume_attachment" "ebs_super_svn_vol_att" {
  device_name                    = "/dev/sdh"
  volume_id                      = aws_ebs_volume.ebs_super_svn_volume.id
  instance_id                    = aws_instance.super.id
  stop_instance_before_detaching = true
}
resource "aws_ebs_volume" "ebs_super_svn_volume" {
  availability_zone = data.aws_subnet.super.availability_zone
  encrypted         = true
  size              = 60
  type              = "gp3"
  tags = {
    Name   = "${var.serial_number}_super_svn"
    Backup = var.environment
  }
  # add additional timeout
  timeouts {
    create = local.create_timeout
    update = local.update_timeout
    delete = local.delete_timeout
  }
}

# Clickhouse volume for super instance
resource "aws_volume_attachment" "ebs_super_clickhouse_vol_att" {
  count                          = 1 # We have to keep the count or else it will recreate the disk
  device_name                    = "/dev/sdi"
  volume_id                      = aws_ebs_volume.ebs_super_clickhouse_volume[0].id
  instance_id                    = aws_instance.super.id
  stop_instance_before_detaching = true
}
resource "aws_ebs_volume" "ebs_super_clickhouse_volume" {
  count             = 1 # We have to keep the count or else it will recreate the disk
  availability_zone = data.aws_subnet.super.availability_zone
  encrypted         = true
  size              = local.keeper_disk_size
  type              = "gp3"
  iops              = var.cmdb_iops
  throughput        = var.cmdb_throughput
  tags = {
    Name = "${var.serial_number}_super_clickhouse"
  }
  # add additional timeout
  timeouts {
    create = local.create_timeout
    update = local.update_timeout
    delete = local.delete_timeout
  }
}
