Resources required for setting up cloud collectors required for benchmarking are defined
in the fsiem_collector folder

# All env variables are optional
export CI_ENVIRONMENT_NAME=playground # dev/playground

# Set the number of collector required for benchmarking
export COLLECTOR_INSTANCE_COUNT=1

# Set the fsiem stack serial number required for benchmarking
export BM_SERIAL_NUMBER=FSMCLD0000000152

# Build what you have
sudo -E bash build/ci-wrapper.sh bm-build

# Deploy this build to env defined by $CI_ENVIRONMENT_NAME
sudo -E bash build/ci-wrapper.sh bm-deploy
