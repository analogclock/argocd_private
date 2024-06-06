output "bm_vpc_id" {
  value       = module.vpc.vpc_id
  description = "BM vpc id"
}
output "bm_vpc_pvt_subnets" {
  value       = module.vpc.private_subnets
  description = "BM vpc private subnets"
}

