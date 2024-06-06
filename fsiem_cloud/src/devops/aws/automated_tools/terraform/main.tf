# Main file to set provider
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.20.1"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = "us-east-1"
}
