from typing import List
from HD_BET.HD_BET.run import run_hd_bet


def RunHDBet_CPU(input_files:[str, List[str]], output_files:str, mode:str = 'accurate', tta=False):
    '''Helper method to call HD bet using the CPU'''

    if mode != "fast" and mode != "accurate":
        raise Exception("Bad mode " + mode)
    
    run_hd_bet(input_files, output_files, mode, device='cpu', pp=False, tta=tta, save_mask=True, overwrite_existing=True, bet=False)
