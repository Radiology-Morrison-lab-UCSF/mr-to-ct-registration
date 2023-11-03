#!/bin/bash

# Currently builds a python environment that is suitable for this
# Does not build an image, and assumes python is available
# Call from the directory containing this project
# And call the following if needed for python 3.9:
#   conda init
#   conda activate # If needed for python 3.9


set -e

# Uncomment if pip complains it can't find a version
# pip3 install --upgrade pip --user


python3.9 -m venv env
source env/bin/activate

# Install ants from a pre-made wheel because other ways are very slow
# and can crash if other dependencies are not available to build it
# from source (like certain versions of CMAKE)
wget https://github.com/ANTsX/ANTsPy/releases/download/v0.3.8/antspyx-0.3.8-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl

python3.9 -m pip install antspyx-0.3.8-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
rm antspyx-0.3.8-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl

#python3 -m pip install --upgrade pip
python3.9 -m pip install -r requirements.txt