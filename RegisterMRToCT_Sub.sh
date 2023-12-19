#!/bin/bash

# Uses python-only singularity image
# Call from outside of singularity
set -e

env/bin/activate
env/bin/python3.10 -m RegisterMRToCT "$@"