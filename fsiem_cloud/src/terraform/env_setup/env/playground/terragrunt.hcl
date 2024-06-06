include "root" {
  path = find_in_parent_folders()
}

inputs = {
  environment              = "playground"
  deployment_bucket        = "fsiem-terraform-ftn"
  deployment_bucket_region = "us-east-1"
}

terraform {
  # Having single slashes is important for deployment. Just ignore terraform warnings - it works. Trust me.
  # With two slashes, the deployment will fail to resolve paths, and an update will actually delete everything.
  # With 4 slashes, it will fail to create resources first time, but subsequent updates work fine.
  source = "../../"
}
