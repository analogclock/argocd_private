/*
  Main file to set provider
*/ terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.20.1"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.region
  default_tags {
    # Includes required infosec tags as listed in this doc:
    # https://fuse.fortinet.com/HigherLogic/System/DownloadDocumentFile.ashx?DocumentFileKey=051af8f5-6198-cfdd-0a14-4a133fb267a3&forceDialog=0
    tags = local.global_tags
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

