import os
from typing import List

class FileLocationsBase:

    def AssertFileFound(self, loc:str):
        if not os.path.exists(loc):
            raise Exception("Missing: " + loc)


class FileLocations_fMRIPrep(FileLocationsBase):

    def __init__(self, dir_subject:str, subjectId:str):
        self.dir_subject = dir_subject
        self.dir_structural = os.path.join(self.dir_subject, "anat")
        self.loc_t1 = os.path.join(self.dir_structural, "sub-" + subjectId.lower() + "_acq-BRAVO_desc-preproc_T1w.nii.gz")
        self.loc_mask_brain = os.path.join(self.dir_structural, "sub-" + subjectId.lower() + "_acq-BRAVO_desc-brain_mask.nii.gz")


    def GetAllFileLocations(self) -> List:
        return [self.loc_t1, self.loc_mask_brain]

    def AssertFilesFound(self):
        for loc in self.GetAllFileLocations():
            self.AssertFileFound(loc)

class FileLocations_LeGui(FileLocationsBase):

    def __init__(self, subject_dir:str):
        self.dir_subject = subject_dir
        self.dir_registered = os.path.join(self.dir_subject, "Registered")
        self.loc_t1 = os.path.join(self.dir_registered, "MR.nii")
        self.loc_mask_gm = os.path.join(self.dir_registered, "MRGray.nii")
        self.loc_mask_wm = os.path.join(self.dir_registered, "MRWhite.nii")
        self.loc_mask_csf = os.path.join(self.dir_registered, "MRCSF.nii")

    def GetAllFileLocations(self) -> List:
        return [self.loc_t1]

    def AssertFilesFound(self):
        for loc in self.GetAllFileLocations():
            self.AssertFileFound(loc)


class FileLocations_LeGuiToFMRI(FileLocationsBase):

    def __init__(self, dir_LgToFMRI:str, subjectId:str):
        self.dir_subject = os.path.join(dir_LgToFMRI, "sub-" + subjectId.lower())
        self.loc_transform_LGToFMRI = os.path.join(self.dir_subject, "LeGUIT1_to_fMRIPrepT1.mat")
        self.loc_t1LG_inFMRISpace = os.path.join(self.dir_subject, "t1_from_LeGUI_in_fMRI_space.nii.gz")
        self.loc_t1fMRIPrep_inLGSpace = os.path.join(self.dir_subject, "t1_from_fMRI_in_LeGUI_space.nii.gz")


    def GetAllFileLocations(self) -> List:
        return [self.loc_transform_LGToFMRI, self.loc_t1LG_inFMRISpace, self.loc_t1fMRIPrep_inLGSpace]

    def CreateDestinationDir(self):
        if not os.path.exists(self.dir_subject):
            os.makedirs(self.dir_subject, exist_ok=True)


