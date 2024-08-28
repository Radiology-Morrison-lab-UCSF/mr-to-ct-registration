#!/bin/bash

set -e


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

dirTop="$(realpath $1)"
locT1="$(realpath $2)"

set -x
cd $SCRIPT_DIR
source env/bin/activate

export PATH=$PATH:"/netopt/rhel7/versions/cuda/cuda-11.2/bin/"
export PATH=$PATH:"/netopt/rhel7/versions/cuda/cuda-11.2/lib64/"


python3.10 -m main --legui $dirTop \
                  --t1 $locT1 \
                  --out $dirTop/fixed_legui/
