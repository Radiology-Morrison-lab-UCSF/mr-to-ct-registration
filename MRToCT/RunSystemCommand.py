from typing import List
import subprocess
import os

def RunCMD(params : List, dir_working:None):
    if dir_working is None:
        dir_working = os.getcwd()

    process = subprocess.run(params, cwd=dir_working, text=True)
    if process.returncode != 0:
        raise Exception(str(params) + " failed " + process.stderr)