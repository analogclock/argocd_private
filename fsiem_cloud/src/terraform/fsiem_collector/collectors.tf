/*
  This is the ec2 instance for the collectors
*/
data "aws_subnet" "collector" {
  count  = var.data_collectors
  vpc_id = data.aws_vpc.bmvpc.id
  filter {
    name   = "tag:Name"
    values = ["bm-playground-private-us-east-1a"]
  }
}

data "aws_ec2_instance_type_offering" "collector" {
  count = var.data_collectors
  filter {
    name   = "instance-type"
    values = var.collector_instance_types
  }
  filter {
    name   = "location"
    values = [data.aws_subnet.collector[count.index].availability_zone_id]
  }
  location_type            = "availability-zone-id"
  preferred_instance_types = var.collector_instance_types
}

resource "aws_instance" "collector" {
  count = var.data_collectors
  ami   = local.siem_ami
  root_block_device {
    encrypted   = true
    volume_size = 25
    volume_type = "gp3"
    tags = merge(
      local.global_tags,
      {
        Name   = "${var.bm_serial_number}_collector_${count.index}_root"
        Backup = var.environment
      }
    )
  }

  iam_instance_profile = aws_iam_instance_profile.instance_profile.id

  instance_type          = data.aws_ec2_instance_type_offering.collector[count.index].id
  subnet_id              = data.aws_subnet.collector[count.index].id
  vpc_security_group_ids = [aws_security_group.collector[0].id]
  user_data = templatefile(
    "install_siem_collector.sh",
    {
      user                     = "ec2-user"
      env                      = var.environment
      serial_no                = var.bm_serial_number
      s3_scripts_bucket        = local.s3_scripts_bucket
      s3_scripts_bucket_region = var.bm_region[var.environment]
    }
  )
  tags = {
    Name = "${var.bm_serial_number}_collector_${count.index}"
    Role = "collector"
  }
  lifecycle {
    ignore_changes = [user_data, ami]
  }
}
# AWS docs suggest /dev/sd[f-p] names for EBS volumes
# opt ebs volume for collector instances
resource "aws_volume_attachment" "ebs_collector_opt_vol_att" {
  count       = var.data_collectors
  device_name = "/dev/sdf"
  volume_id   = aws_ebs_volume.ebs_collector_opt_volume[count.index].id

  instance_id                    = aws_instance.collector[count.index].id
  stop_instance_before_detaching = true
}

resource "aws_ebs_volume" "ebs_collector_opt_volume" {
  count             = var.data_collectors
  availability_zone = data.aws_subnet.collector[count.index].availability_zone
  encrypted         = true
  size              = 100
  type              = "gp3"
  tags = merge(
    local.global_tags,
    {
      Name   = "${var.bm_serial_number}_collector_${count.index}_opt"
      Backup = var.environment
    }
  )
  # add additional timeout
  timeouts {
    create = local.create_timeout
    update = local.update_timeout
    delete = local.delete_timeout
  }

}
