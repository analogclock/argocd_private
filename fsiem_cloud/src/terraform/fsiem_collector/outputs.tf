output "collector_instance_count" {
  value       = var.data_collectors
  description = "No of collectors deployed"
}

output "bm_serial_no" {
  value       = var.bm_serial_number
  description = "BM stack serial number"
}
output "collector_ip" {
  value       = join(" ", aws_instance.collector.*.private_ip)
  description = "Collector ip addresses"

}

