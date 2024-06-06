# Use the script in src/devops/aws/get_ami_ids.sh to generate a list of amis

# FortiSIEM-VA-7.1.5.0181-Release-BYOL-912b1c1e-032b-483c-b3f4-61f370288274
locals {
  siem_ami = var.environment == "prod" ? local.siem_ami_prod[var.region] : local.siem_ami_dev[var.region]
  # siem ami used in production
  # https://aws.amazon.com/marketplace/pp/prodview-6rqkoxup67mhq
  siem_ami_prod = {
    "af-south-1"     = "ami-0934ea9077ecd6758"
    "ap-south-1"     = "ami-0762f0dfb32cd526f"
    "eu-north-1"     = "ami-0e865c6fbe35eab34"
    "eu-west-3"      = "ami-03fc6a46a1285aad1"
    "eu-west-2"      = "ami-048ee2e029b360d54"
    "eu-west-1"      = "ami-07066055f54971a0b"
    "ap-northeast-3" = "ami-05cd457dce8a985fe"
    "ap-northeast-2" = "ami-01c88463c6b9bfa3d"
    "me-south-1"     = "ami-020a79672b4ce666c"
    "ap-northeast-1" = "ami-032b1f028db585d98"
    "ca-central-1"   = "ami-02fcbc2bc71325808"
    "sa-east-1"      = "ami-03d1255ead05b6f4f"
    "ap-east-1"      = "ami-0d6268a0de5e4ef2e"
    "ap-southeast-1" = "ami-0ec7d533b40476f74"
    "ap-southeast-2" = "ami-00c793f3dfda54a80"
    "eu-central-1"   = "ami-0e85e2bebce70a0b0"
    "us-east-1"      = "ami-087487a990aa8bf5c"
    "us-east-2"      = "ami-07e180421ac811405"
    "us-west-1"      = "ami-023d24d5f325dfd5d"
    "us-west-2"      = "ami-003b6d4e03c71057a"
  }
  # siem ami used in dev and playground
  # FortiSIEM-VA-7.2.0.2598 in us-east-1
  siem_ami_dev = {
    "af-south-1"     = "ami-0934ea9077ecd6758"
    "ap-south-1"     = "ami-0762f0dfb32cd526f"
    "eu-north-1"     = "ami-0e865c6fbe35eab34"
    "eu-west-3"      = "ami-03fc6a46a1285aad1"
    "eu-west-2"      = "ami-048ee2e029b360d54"
    "eu-west-1"      = "ami-07066055f54971a0b"
    "ap-northeast-3" = "ami-05cd457dce8a985fe"
    "ap-northeast-2" = "ami-01c88463c6b9bfa3d"
    "me-south-1"     = "ami-020a79672b4ce666c"
    "ap-northeast-1" = "ami-032b1f028db585d98"
    "ca-central-1"   = "ami-02fcbc2bc71325808"
    "sa-east-1"      = "ami-03d1255ead05b6f4f"
    "ap-east-1"      = "ami-0d6268a0de5e4ef2e"
    "ap-southeast-1" = "ami-0ec7d533b40476f74"
    "ap-southeast-2" = "ami-00c793f3dfda54a80"
    "eu-central-1"   = "ami-0e85e2bebce70a0b0"
    "us-east-1"      = "ami-0ad7474bb0a90cdda"
    "us-east-2"      = "ami-07e180421ac811405"
    "us-west-1"      = "ami-023d24d5f325dfd5d"
    "us-west-2"      = "ami-003b6d4e03c71057a"
  }
}
