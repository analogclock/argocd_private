# Use the script in src/devops/aws/get_aws_regions.sh to generate a list of regions
# Timezones are typed manually, as there is no way that I (OM) found to get timezones for
# the regions.

# Note, not all cities are pesent in the IANA database.
# To test a new region, you can use this command on Linux:
# TZ=":America/New_York" date +%z

locals {

  region_tz = local.region_tz_map[var.region]

  # A map of AWS region name => # IANA timezone expressed as geographic region/city
  region_tz_map = {
    "af-south-1"     = "Africa/Johannesburg"
    "ap-east-1"      = "Asia/Hong_Kong"
    "ap-northeast-1" = "Asia/Tokyo"
    "ap-northeast-2" = "Asia/Seoul"
    "ap-northeast-3" = "Asia/Tokyo"
    "ap-south-1"     = "Asia/Kolkata"
    "ap-southeast-1" = "Asia/Singapore"
    "ap-southeast-2" = "Australia/Sydney"
    "ca-central-1"   = "America/Montreal"
    "eu-central-1"   = "Europe/Berlin"
    "eu-north-1"     = "Europe/Stockholm"
    "eu-west-1"      = "Europe/Dublin"
    "eu-west-2"      = "Europe/London"
    "eu-west-3"      = "Europe/Paris"
    "me-south-1"     = "Asia/Bahrain"
    "sa-east-1"      = "America/Sao_Paulo"
    "us-east-1"      = "America/New_York"
    "us-east-2"      = "America/New_York"
    "us-west-1"      = "America/Los_Angeles"
    "us-west-2"      = "America/Los_Angeles"
  }
}
