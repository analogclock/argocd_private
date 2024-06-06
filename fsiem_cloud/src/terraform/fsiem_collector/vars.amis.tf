# Use the script in src/devops/aws/get_ami_ids.sh to generate a list of amis

# FortiSIEM-VA-6.7.3.1729-Release-BYOL-912b1c1e-032b-483c-b3f4-61f370288274
locals {
  siem_ami = local.siem_ami_dev[var.region]

  # siem ami used in dev and playground
  siem_ami_dev = {
    "ap-south-1"     = "ami-0e7f69d4d15b0d94d"
    "eu-north-1"     = "ami-037b63aaae9b64dc3"
    "eu-west-3"      = "ami-0812b05799738c57d"
    "eu-west-2"      = "ami-063f329078f8f6fa7"
    "eu-west-1"      = "ami-020b09c1dd8704de3"
    "ap-northeast-3" = "ami-056ccf0b4526dd7ae"
    "ap-northeast-2" = "ami-07b30bb4538ddfa1a"
    "me-south-1"     = "ami-0eabfb43f85c114bb"
    "ap-northeast-1" = "ami-026224b50ea79a7ab"
    "ca-central-1"   = "ami-02eabc3b0dfc6a4e1"
    "sa-east-1"      = "ami-0e6000587298ebce6"
    "ap-southeast-1" = "ami-0c1f5c3cd691cccd9"
    "ap-southeast-2" = "ami-0fcbe2afaa9ab5af1"
    "eu-central-1"   = "ami-0eb03a048f4b88557"
    "us-east-1"      = "ami-069d86a5fbed37852"
    "us-east-2"      = "ami-0561d9ac0926a5b7e"
    "us-west-1"      = "ami-00403bd127c0444c1"
    "us-west-2"      = "ami-03e148fccc7862d30"
  }
}
