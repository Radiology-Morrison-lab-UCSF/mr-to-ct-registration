#!/bin/bash
# Builds this with only python in the container, and it using these files externally

set -e

singularity build --fakeroot --bind `pwd`:/script python-only.sif build-as-apptainer/python-only.def

# Now build the env folder
singularity exec --cleanenv --bind /data python-only.sif ./build.sh python3.10
chmod -R 777 env/bin/