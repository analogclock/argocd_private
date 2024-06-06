#!/bin/bash -e
# File with utility functions, from root of the project, use it like
# source build/utilities.sh

# Parse simple YAML in bash, from https://stackoverflow.com/a/21189044/706456
# This is handy as we don't need to install yq.
function parse_yaml {
   local prefix=$2
   local s='[[:space:]]*'
   local w='[a-zA-Z0-9_]*'
   local fs
   fs=$(echo @ | tr @ '\034')
   sed -ne "s|^\($s\):|\1|" \
        -e "s|^\($s\)\($w\)$s:${s}[\"']\(.*\)[\"']$s\$|\1$fs\2$fs\3|p" \
        -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p" "$1" |
   awk -F "$fs" '{
      indent = length($1)/2;
      vname[indent] = $2;
      for (i in vname) {if (i > indent) {delete vname[i]}}
      if (length($3) > 0) {
         vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
         printf("%s%s%s=\"%s\"\n", "'"${prefix}"'",vn, $2, $3);
      }
   }'
}

# Download and install software
install_binary_from_url() {
  local url="${1?unknown_arg_url}"   # 1st arg: source URL
  local file="${2?unknown_arg_file}" # 2nd arg: file name
  curl -fsSL "$url" > "${file}"
  chmod +x "${file}"
  mv "${file}" "/usr/bin/${file}"
}

# Download, unzip, and install software
install_zipped_binary_from_url() {
  local url="${1?unknown_arg_url}"            # 1st arg: source URL
  local file="${2?unknown_arg_file}"          # 2nd arg: file name

  local zip_file="${file}.zip"

  curl -fsSL "$url" > "${zip_file}"
  unzip -qq "${zip_file}"
  chmod +x "${file}"
  mv "${file}" "/usr/bin/${file}"

  rm -f "${zip_file}"
  rm -rf "${file:?unknown_arg_file}/*"
}

# Use this to create SLUG variables - those are safe for use in URLs
# Based on https://stackoverflow.com/a/44811468/706456
# Using gitlab slug conversion https://docs.gitlab.com/ee/ci/variables/predefined_variables.html.
# Lowercased, shortened to 63 bytes, and with everything except 0-9 and a-z replaced with -.
# No leading or trailing -.
sanitize() {
   local s="${1?need a string}" # receive input in first argument
   s="${s//[^[:alnum:]]/-}"     # replace all non-alnum characters to -
   s="${s//+(-)/-}"             # convert multiple - to single -
   s="${s/#-}"                  # remove - from start
   s="${s/%-}"                  # remove - from end
   s="${s,,}"                   # convert to lowercase
   echo "${s:0:62}"             # shorten to 63 bytes
}

# Utility function: check if the first arg contains the second arg. Exits with 0 if contains.
# From https://stackoverflow.com/a/8063284/706456
contains() {
  echo "$1" | grep -w -q "$2"
}

# Returns percent of disk used for a root mount point - "/"
#
#   Get disk usage, select columns with usage and mount name,
#   find root mount "/", ensure we only get one last entry,
#   extract number value (percent of disk used)
root_vol_disk_usage_percent() {
  df | awk '{ print $5, $6 }' | grep -w "/" | tail -n 1 | cut -d'%' -f1
}

print_root_vol_disk_usage()
{
  echo "----------"
  df -h | head -n 1
  df -h | grep -w "/"
  echo "----------"
}

# Get remote object's file size in human readable form via aws s3 and cut
function remote_file_size() {
  aws s3 ls "$1" --human-readable | cut -d\  -f4,5
}
