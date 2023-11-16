from typing import List
import torch # Fix weird issue that causes crash when run imported
from HD_BET.run import run_hd_bet
import tempfile


def RunHDBet_CPU(input_files:[str, List[str]], mode:str = 'fast', tta=False):
    '''Helper method to call HD bet using the CPU. Returns the mask'''

    if mode != "fast" and mode != "accurate":
        raise Exception("Bad mode " + mode)
    
    loc_out = tempfile.mktemp(suffix="nii.gz")

    return run_hd_bet(input_files, 
                        loc_out, 
                        mode, 
                        config_file=None, 
                        device='cpu', 
                        postprocess=True, 
                        do_tta=tta, 
                        keep_mask=False, 
                        overwrite=True, 
                        bet=False)[0]
