# overview

This modules separates bucket creation for clickhouse data

# How to use

In any terraform code that you want to include it simply use the following:

```terraform
module "name" {
 source = "./modules/clickhouse_archive"
 bucket_name = "my_clickhouse_archive"
 providers {
  aws = aws.client
 }
}
```
