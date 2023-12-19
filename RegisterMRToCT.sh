#!/bin/bash

# Uses python-only singularity image
# Call from outside of singularity

singularity exec --cleanenv --bind /data python-only.sif ./RegisterMRToCT_Sub.sh "$@"