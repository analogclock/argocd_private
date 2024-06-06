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
  default_tags {
    tags = local.global_tags
  }
}

# Additional region access
provider "aws" {
  region = "us-east-2"
  alias  = "us-east-2"
  default_tags {
    tags = local.global_tags
  }
}

provider "aws" {
  region = "us-west-2"
  alias  = "us-west-2"
  default_tags {
    tags = local.global_tags
  }
}

provider "aws" {
  alias  = "eu-central-1"
  region = "eu-central-1"
  default_tags {
    tags = local.global_tags
  }
}

provider "aws" {
  alias  = "eu-west-1"
  region = "eu-west-1"
  default_tags {
    tags = local.global_tags
  }
}

provider "aws" {
  alias  = "eu-west-2"
  region = "eu-west-2"
  default_tags {
    tags = local.global_tags
  }
}

provider "aws" {
  alias  = "eu-west-3"
  region = "eu-west-3"
  default_tags {
    tags = local.global_tags
  }
}

provider "aws" {
  alias  = "eu-north-1"
  region = "eu-north-1"
  default_tags {
    tags = local.global_tags
  }
}

provider "aws" {
  alias  = "ca-central-1"
  region = "ca-central-1"
  default_tags {
    tags = local.global_tags
  }
}

provider "aws" {
  alias  = "ap-south-1"
  region = "ap-south-1"
  default_tags {
    tags = local.global_tags
  }
}

provider "aws" {
  alias  = "ap-southeast-1"
  region = "ap-southeast-1"
  default_tags {
    tags = local.global_tags
  }
}

provider "aws" {
  alias  = "ap-southeast-2"
  region = "ap-southeast-2"
  default_tags {
    tags = local.global_tags
  }
}

provider "aws" {
  alias  = "me-south-1"
  region = "me-south-1"
  default_tags {
    tags = local.global_tags
  }
}

provider "aws" {
  alias  = "af-south-1"
  region = "af-south-1"
  default_tags {
    tags = local.global_tags
  }
}

provider "aws" {
  alias  = "ap-east-1"
  region = "ap-east-1"
  default_tags {
    tags = local.global_tags
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}
