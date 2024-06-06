#!/bin/bash -e

# Provider and module cache for tf providers
if [[ -z "${NEXUS_TERRAFORM_PROXY}" ]]; then
  echo "NEXUS_TERRAFORM_PROXY is not set. Accessing terraform registry directly"
else
  echo "NEXUS_TERRAFORM_PROXY is set to ${NEXUS_TERRAFORM_PROXY}"
  # output the file we need, and use it
  cat << EOF >"$HOME"/config.tfrc
provider_installation {
  direct {
      exclude = ["registry.terraform.io/*/*"]
  }
  network_mirror {
      url = "${NEXUS_TERRAFORM_PROXY}"
  }
}
EOF

  echo "Content of $HOME/config.tfrc"
  cat "$HOME/config.tfrc"
  export TF_CLI_CONFIG_FILE=$HOME/config.tfrc
  echo "using TF_CLI_CONFIG_FILE=${TF_CLI_CONFIG_FILE}"
fi
mkdir -p ~/.terraform.d/plugin-cache
echo "plugin_cache_dir   = \"$HOME/.terraform.d/plugin-cache\"" > ~/.terraformrc

if [[ -z "${NEXUS_TERRAFORM_PROXY}" ]]; then
  echo "NEXUS_TERRAFORM_PROXY is not set... Accessing terraform registry directly"
else
  if [[ -f "ec2/override.tf" ]]; then
    echo "override already exists, a build has happened before and is using the proxy"
  else
    # we need to check if we want to use the proxy
    if [[ -f "ec2/override.tf.proxy" ]]; then
      # may not exist when running in env_setup
      # as no modules are required.
      echo "override.tf.proxy exists"
      cp ec2/override.tf.proxy ec2/override.tf
      echo "NEXUS_TERRAFORM_PROXY is set, will use override.tf"
    else
      echo "Override proxy does not exists -- will not copy or use proxy"
    fi
  fi
fi

(cd ec2 && terraform init -no-color -upgrade)

# Remove override.tf, as during deploy terragrunt will poll the source (jfrog/terraform.io)
# for the latest versions. And if its still pointed at jfrog at deploy then it will fail
rm -f ec2/override.tf
