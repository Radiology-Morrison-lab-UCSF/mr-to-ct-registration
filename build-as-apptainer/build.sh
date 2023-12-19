#!/bin/bash
# Run from the top directory of this solution
# Delete any local virtual environments before starting or
# suffer a long build time


# remove __pycache__
find . -type d -name __pycache__ -exec rm -r "{}" \;

set -e
# rm -f ./fix-legui.sif
# singularity build --fakeroot /dev/shm/fix-legui.sif build-as-apptainer/definition.def
# mv /dev/shm/fix-legui.sif ./fix-legui.sif

rm -f ./reg-mr-to-ct.sif
singularity build --fakeroot /dev/shm/reg-mr-to-ct.sif build-as-apptainer/mr-to-ct.def
mv /dev/shm/reg-mr-to-ct.sif ./reg-mr-to-ct.sif

