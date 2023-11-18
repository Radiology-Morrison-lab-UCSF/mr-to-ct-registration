from PythonUtils.filelocations import FileLocationsBase
import os
from PythonUtils.IO import FindNiftiOrGzPath

class LeGuiFileLocations(FileLocationsBase):
    '''
    Describes file locations in LeGUI
    '''

    def __init__(self, dir_subject):
        self.dir_results = os.path.join(dir_subject, "Registered")
        self.loc_CT = FindNiftiOrGzPath(os.path.join(self.dir_results, "CT.nii"))
        self.loc_electrodes = os.path.join(self.dir_results, "Electrodes.mat")


    def AssertCTFound(self):
        self.AssertFileFound(self.loc_CT)

    def AssertElectrodesFound(self):
        self.AssertFileFound(self.loc_CT)