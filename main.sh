#!/bin/bash

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

dirTop="$(realpath $1)"
locT1="$(realpath $2)"

set -x
cd $SCRIPT_DIR
source env/bin/activate

python3.9 -m main --legui $dirTop \
                  --t1 $locT1 \
                  --out $dirTop/fixed_legui/