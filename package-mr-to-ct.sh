#!/bin/bash
# Packages this up as a standalone executable
# Do NOT have .env activated when running this

#python3.9 -m pip install -U nuitka
#conda install libpython-static

#python3.9 ~/.local/bin/nuitka3 --standalone --main=RegisterMRToCT --include-data-dir="../HDBET/HD_BET/hd-bet_params/"


# cd to the building environment

# enter it

singularity shell --writable --fakeroot --bind /data/:/data mycontainer

# then run the following

loc=`pwd`

# ------ WITH CONDA AVAIL

conda activate
conda install python-dev -y

# ------ NO CONDA AVAIL

mkdir -p ~/patchelf/ 
cd ~/patchelf
wget "https://github.com/NixOS/patchelf/releases/download/0.18.0/patchelf-0.18.0-x86_64.tar.gz"
gunzip *.tar.gz
tar -xf *.tar
export PATH=$PATH:~/home/patchelf/bin/

# ------


cd $loc

./build python3.10 .nuitka-env

source .nuitka-env/bin/activate
python3.10 -m pip install nuitka
python3.10 -m nuitka --standalone --main=main.py --static-libpython=no