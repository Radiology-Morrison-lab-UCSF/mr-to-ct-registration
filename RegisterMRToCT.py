from MRToCT.RegisterMRToCTPipeline import RegisterMRToCTPipeline
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""Registers a T1 MR to a same-subject CT""")
    parser.add_argument('--t1', dest='loc_t1', action='store', required=True, help="Full path to the T1 image")
    parser.add_argument('--ct', dest='loc_ct', action='store', required=True, help="Full path to the CT image")
    parser.add_argument('--gpu', action="store_true", default=False, help="Whether to use the GPU for skull stripping (much faster)")
    parser.add_argument('--no-bias-corr', dest='noBiasCorrection', action="store_false", default=False, help="Does NOT apply bias correction to the T1 when this flag is specified.")
    parser.add_argument('--out', dest='dir_out', action='store', required=True, help="Full path to a directory to output to. Created if not found.")
    parser.add_argument('--out-prefix', dest='outPrefix', action='store', default="", help="Prepended to all output files to avoid name clashes")

    args = parser.parse_args()

    pipeline = RegisterMRToCTPipeline(mrImgOrLocation=args.loc_t1,
                                      ctImgOrLocation=args.loc_ct,
                                    dir_output=args.dir_out,
                                    useGPU=args.gpu,
                                    prefix=args.outPrefix,
                                    applyN4Correction=not args.noBiasCorrection)
    pipeline.Run()