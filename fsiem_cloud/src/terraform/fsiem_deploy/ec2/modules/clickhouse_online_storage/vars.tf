variable "number_of_data_volumes" {
  description = "Number of data volumes to create and attach"
  default     = 1
  validation {
    condition     = var.number_of_data_volumes >= 1 && var.number_of_data_volumes <= 6
    error_message = "number of data volumes must be between 1 and 6"
  }
}

variable "worker_instance_id" {
  description = "Given worker id to attach volumes to"
}

variable "data_worker_volume_size_gb" {
  default = 500
}

variable "data_worker_volume_throughput" {
  default = 125
}

variable "data_worker_volume_iops" {
  default = 3000
}

variable "data_disk_name_prefix" {
}

variable "worker_availability_zone" {
}

variable "disk_create_timeout" {
  default = 300
}

variable "disk_delete_timeout" {
  default = 300
}

variable "disk_update_timeout" {
  default = 300
}
