/*
  Systems Manager
*/

resource "aws_ssm_association" "inventory" {
  association_name = var.environment
  name             = "AWS-GatherSoftwareInventory"
  targets {
    key    = "tag:Environment"
    values = [var.environment]
  }
  parameters = {
    applications                = "Enabled"
    awsComponents               = "Enabled"
    customInventory             = "Enabled"
    instanceDetailedInformation = "Enabled"
    networkConfig               = "Enabled"
  }
  schedule_expression = "rate(1 day)"
}

resource "aws_ssm_association" "inventory_ca_central_1" {
  provider         = aws.ca-central-1
  association_name = var.environment
  name             = "AWS-GatherSoftwareInventory"
  targets {
    key    = "tag:Environment"
    values = [var.environment]
  }
  parameters = {
    applications                = "Enabled"
    awsComponents               = "Enabled"
    customInventory             = "Enabled"
    instanceDetailedInformation = "Enabled"
    networkConfig               = "Enabled"
  }
  schedule_expression = "rate(1 day)"
}

resource "aws_ssm_association" "inventory_eu_west_1" {
  provider         = aws.eu-west-1
  association_name = var.environment
  name             = "AWS-GatherSoftwareInventory"
  targets {
    key    = "tag:Environment"
    values = [var.environment]
  }
  parameters = {
    applications                = "Enabled"
    awsComponents               = "Enabled"
    customInventory             = "Enabled"
    instanceDetailedInformation = "Enabled"
    networkConfig               = "Enabled"
  }
  schedule_expression = "rate(1 day)"
}

resource "aws_ssm_association" "inventory_us_west_2" {
  provider         = aws.us-west-2
  association_name = var.environment
  name             = "AWS-GatherSoftwareInventory"
  targets {
    key    = "tag:Environment"
    values = [var.environment]
  }
  parameters = {
    applications                = "Enabled"
    awsComponents               = "Enabled"
    customInventory             = "Enabled"
    instanceDetailedInformation = "Enabled"
    networkConfig               = "Enabled"
  }
  schedule_expression = "rate(1 day)"
}
