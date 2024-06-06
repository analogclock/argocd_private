# overview

This module adds online storage to workers, to allow us to loop a set of disks

# How to use

In any terraform code that you want to include it simply use the following:

```terraform
module "clickhouse_data_attachment" {
  source = "./modules/clickhouse_online_storage/"
  count  = var.data_workers

  number_of_data_volumes        = var.data_disk_count
  data_disk_name_prefix         = "${var.serial_number}_worker_${count.index}_clickhouse"
  data_worker_volume_iops       = var.data_disk_iops
  data_worker_volume_throughput = var.data_disk_throughput
  data_worker_volume_size_gb    = var.data_disk_size
  disk_create_timeout           = local.create_timeout
  disk_delete_timeout           = local.delete_timeout
  disk_update_timeout           = local.update_timeout
  worker_availability_zone      = data.aws_subnet.worker[count.index].availability_zone
  worker_instance_id            = aws_instance.worker[count.index].id
}
```
