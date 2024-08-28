import argparse
import os
from MRToCT.FixLeguiRegistration import FixLeguiRegistration


parser = argparse.ArgumentParser(description="""Fixes LeGUI registrations and flipping issues. Results appear in a new directory leaving LeGUI results 'as-is'.""")
parser.add_argument('--gpu', action="store_true", default=False)
parser.add_argument('--legui', dest='dir_legui', action='store', required=True, help="Full path to the legui directory containing the CT file")
parser.add_argument('--t1', dest='loc_t1', action='store', required=True, help="Full path to the T1 image in native space, or similar (NOT the LeGUI MR image)")
parser.add_argument('--out', dest='dir_out', action='store', required=True, help="Full path to a directory to output to. Created if not found.")

args = parser.parse_args()


pipeline = FixLeguiRegistration(args.loc_t1,
                                args.dir_legui, 
                                args.dir_out,
                                useGPU=args.gpu)
pipeline.keepIntermediates = True
pipeline.Run()
