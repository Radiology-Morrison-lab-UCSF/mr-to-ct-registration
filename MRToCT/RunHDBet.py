from typing import List
import HDBET.HD_BET.run
import tempfile

def RunHDBet_CPU(input_files:[str, List[str]], mode:str = 'fast', tta=False):
    '''Helper method to call HD bet using the CPU. Returns the mask'''

    if mode != "fast" and mode != "accurate":
        raise Exception("Bad mode " + mode)
    
    loc_out = tempfile.mktemp(suffix="nii.gz")

    return HDBET.HD_BET.run.run_hd_bet(input_files, 
                                       loc_out, 
                                       mode, 
                                       config_file=None, 
                                       device='cpu', 
                                       postprocess=True, 
                                       do_tta=tta, 
                                       keep_mask=False, 
                                       overwrite=True, 
                                       bet=False)[0]
