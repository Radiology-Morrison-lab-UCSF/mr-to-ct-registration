# MR to CT Registration

This was developed to properly register CT to MR images, and to fix issues with LeGui with bad-registrations and flipped MR images.

It contains two main entry points. One to fix legui, another to run a MR to CT registration

## Building

You only need to do this once!

### Cluster, no Python 3.9 available

This requires Python 3.9 or later. To run this on the cluster, where this is not available, it's easiest to

1. build a singularity image that contains Python 3.10
1. Run that image with `exec`, with file path bindings back to this source code to set up a python environment
1. Run that image with `exec`, with the above binddings to this source code, and to `/data/` to process data

To build the image:

1. `cd` to the top directory of this solution
1. In bash: `build-as-apptainer/build-python-only.sh`


### With Python 3.9 or later available

Build the environment (once only)

`/.build.sh`

## Running

### Register MR to CT
#### Cluster, no Python 3.9 available

`./RegisterMRToCT.sh --t1 path-to-your-t1.nii --ct path-to-your-ct.nii --out path-to-a-directory-to-save-to`

#### With Python 3.9 or 3.10 available

```
# Activate once per session
env/bin/activate

# Run with Python
env/bin/python3.10 -m RegisterMRToCT
```

### Fix Legui

Check `main.sh` and `main.py` for details

#### Cluster, no Python 3.9 available

Not implemented.

#### With Python 3.9 available

`./main.sh /directory/containing/legui/folder /path/to/t1`

will output to  `/directory/containing/legui/fixed_legui/`
