#!/bin/bash
set -e

# Currently builds a python environment that is suitable for this
# Does not build an image, and assumes python is available
# Call from the directory containing this project
# And call the following if needed for python 3.9:
#conda init bash
#conda activate # If needed for python 3.9



# Uncomment if pip complains it can't find a version
# pip3 install --upgrade pip --user

echo 'Creating Environment'
python3.9 -m venv env
source env/bin/activate

# Install ants from a pre-made wheel because other ways are very slow
# and can crash if other dependencies are not available to build it
# from source (like certain versions of CMAKE)
if ! python3.9 -m pip show antspyx --require-virtualenv; then
    echo 'Installing ants'
    wget https://github.com/ANTsX/ANTsPy/releases/download/v0.3.8/antspyx-0.3.8-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl

    python3.9 -m pip install antspyx-0.3.8-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl  --require-virtualenv
    rm antspyx-0.3.8-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
fi

#python3 -m pip install --upgrade pip

echo 'Installing immediate requirements'
python3.9 -m pip install -r requirements.txt --require-virtualenv

echo 'Installing PythonUtils'
if [ ! -d "PythonUtils" ]; then
    git clone git@git.ucsf.edu:lee-reid/PythonUtils.git
fi

PythonUtils/build.sh


# HD-BET
if [ ! -d "HDBET" ]; then
    git clone git@git.ucsf.edu:lee-reid/HD-BET-for-python.git HDBET
fi

HDBET/build.sh
