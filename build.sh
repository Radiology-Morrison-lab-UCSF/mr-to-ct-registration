#!/bin/bash
set -ex

# Currently builds a python environment that is suitable for this
# Does not build an image, and assumes python is available
# Call from the directory containing this project
# And call the following if needed for python 3.9:
#conda init bash
#conda activate # If needed for python 3.9

if [ -z "$1" ]; then
    python="python3.9"
else
    python="$1"
fi


if [ -z "$2" ]; then
    envName="env"
else
    envName="$2"
fi


# Uncomment if pip complains it can't find a version
# pip3 install --upgrade pip --user

echo 'Creating Environment'
$python -m venv $envName
source $envName/bin/activate

# Install ants from a pre-made wheel because other ways are very slow
# and can crash if other dependencies are not available to build it
# from source (like certain versions of CMAKE)


install_ants_from_wheel(){
    if ! $python -m pip show antspyx --require-virtualenv; then
        echo 'Installing ants'

        # Check if $py ends with 3.10
        if [[ $python == *3.10 ]]; then
            # Set antsWheel to the specific URL for 3.10
            antsWheel="https://github.com/ANTsX/ANTsPy/releases/download/v0.4.2/antspyx-0.4.2-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"
        # Check if $py ends with 3.9
        elif [[ $python == *3.9 ]]; then
            # Set antsWheel to the specific URL for 3.9
            antsWheel="https://github.com/ANTsX/ANTsPy/releases/download/v0.3.8/antspyx-0.3.8-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"
        else
            echo "Error: Python version not supported. Please use Python 3.10 or 3.9, or update this script at the location of this error message"
            exit 1
        fi


        fn_wheel=$(basename "$antsWheel")
        wget $antsWheel -O $fn_wheel

        $python -m pip install $fn_wheel  --require-virtualenv
        rm $fn_wheel
    fi
}

set +e
trap "echo failed to install ants from wheel. Trying with pip" ERR
install_ants_from_pip
set -e
if [ $? -ne 0]; then
    pip install antspyx     
fi


#python3 -m pip install --upgrade pip

echo 'Installing immediate requirements'
$python -m pip install -r requirements.txt --require-virtualenv

echo 'Installing PythonUtils'
if [ ! -d "PythonUtils" ]; then
    git clone git@git.ucsf.edu:lee-reid/PythonUtils.git
fi

PythonUtils/build.sh $python


echo "done"