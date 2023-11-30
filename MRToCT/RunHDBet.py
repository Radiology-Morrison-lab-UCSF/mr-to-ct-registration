from typing import List
import torch # Fix weird issue that causes crash when run imported
from HD_BET.run import run_hd_bet
import tempfile


def RunHDBet_CPU(input_files:[str, List[str]], mode:str = 'fast', tta=False):
    '''Helper method to call HD bet using the CPU. Returns the mask'''
    return RunHDBet(input_files, 'cpu', mode,tta)


def RunHDBet_GPU(input_files:[str, List[str]], mode:str = 'accurate', tta=True):
    '''Helper method to call HD bet using the GPU. Returns the mask'''
    return RunHDBet(input_files, 0, mode,tta)


def RunHDBet(input_files:[str, List[str]], device, mode:str = 'fast', tta=False):
    '''Helper method to call HD bet using the CPU. Returns the mask'''

    if mode != "fast" and mode != "accurate":
        raise Exception("Bad mode " + mode)
    
    loc_out = tempfile.mktemp(suffix="nii.gz")
    print("device:", device)
    return run_hd_bet(input_files, 
                        loc_out, 
                        mode, 
                        config_file=None, 
                        device=device, 
                        postprocess=True, 
                        do_tta=tta, 
                        keep_mask=False, 
                        overwrite=True, 
                        bet=False)[0]
