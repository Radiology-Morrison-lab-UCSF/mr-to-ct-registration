#!/bin/bash

# Uses python-only singularity image
# Call from outside of singularity

singularity exec --cleanenv --bind /data $(dirname $0)/python-only.sif $(dirname $0)/RegisterMRToCT_Sub.sh "$@"