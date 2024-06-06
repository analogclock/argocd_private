# Create EBS volumes for managing Clickhouse data on workers
# this provides us a way to do nested loops a little simpler
# we require a nested loop here, because we have 2 dimensions
# dimension 1 = the number of workers to create
# dimension 2 = the number of volumes to attach per worker
# this cannot easily be done in a single terraform
# so we introduce a module to handle the volume creation and attachment

locals {
  # device list based on max number of volumes being 6
  device_names = [
    "/dev/sdg",
    "/dev/sdh",
    "/dev/sdi",
    "/dev/sdj",
    "/dev/sdk",
    "/dev/sdl",
  ]
}

# create volumes required to store data
resource "aws_ebs_volume" "ebs_worker_clickhouse_volume" {
  availability_zone = var.worker_availability_zone
  encrypted         = true
  size              = var.data_worker_volume_size_gb
  type              = "gp3"
  count             = var.number_of_data_volumes
  throughput        = var.data_worker_volume_throughput
  iops              = var.data_worker_volume_iops
  tags = {
    Name = "${var.data_disk_name_prefix}_${count.index}"
  }

  # add additional timeout
  timeouts {
    create = var.disk_create_timeout
    update = var.disk_update_timeout
    delete = var.disk_delete_timeout
  }
}

# attach volume to the required instance
resource "aws_volume_attachment" "ebs_worker_clickhouse_vol_att" {
  device_name                    = element(local.device_names, count.index)
  count                          = var.number_of_data_volumes
  volume_id                      = aws_ebs_volume.ebs_worker_clickhouse_volume[count.index].id
  instance_id                    = var.worker_instance_id
  stop_instance_before_detaching = true
}
