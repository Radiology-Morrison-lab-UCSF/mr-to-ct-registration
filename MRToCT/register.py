import os
import ants
from filelocations import FileLocations_LeGui, FileLocations_fMRIPrep, FileLocations_LeGuiToFMRI



class LeguiTofMRIPrepRegistrationPipeline:

    def __init__(self, dir_top:str, subjectId:str):
        dir_legui = os.path.join(dir_top, "LeGUI", subjectId)
        dir_fmri = os.path.join(dir_top, "fmri_prep", "sub-" + subjectId.lower())
        self.locs_legui = FileLocations_LeGui(dir_legui)
        self.locs_fmri = FileLocations_fMRIPrep(dir_fmri, subjectId)
        self.locs_out = FileLocations_LeGuiToFMRI(os.path.join(dir_top, "legui_to_fmri"), subjectId)

    def Run(self):
        self._PrerunChecks()

        t1_LGSpace = ants.image_read(self.locs_legui.loc_t1)
        t1_fMRISpace = ants.image_read(self.locs_fmri.loc_t1)

        self._RegisterAndSave(t1_LGSpace, t1_fMRISpace)

        ants.apply_transforms(fixed=t1_fMRISpace, 
                              moving=t1_LGSpace, 
                              transformlist=[self.locs_out.loc_transform_LGToFMRI]
                              ).to_filename(self.locs_out.loc_t1LG_inFMRISpace)

        ants.apply_transforms(fixed=t1_LGSpace, 
                              moving=t1_fMRISpace, 
                              transformlist=[self.locs_out.loc_transform_LGToFMRI],
                              whichtoinvert=[True]
                              ).to_filename(self.locs_out.loc_t1fMRIPrep_inLGSpace)


        self.Log("Complete")


    def _PrerunChecks(self):
        self.Log("Pre-run checks running.")
        self.locs_legui.AssertFilesFound()
        self.locs_fmri.AssertFilesFound()
        self.Log("Pre-run checks passed.")


    def _RegisterAndSave(self, t1_LGSpace, t1_fMRISpace):
        if os.path.exists(self.locs_out.loc_transform_LGToFMRI):
            self.Log("Registration result found, step skipped.")
            return
        
        
        brainmask_LG = self.GetBrainMask_LGSpace()
        brainmask_fmri = ants.image_read(self.locs_fmri.loc_mask_brain)
        transforms = self._Register(moving=t1_LGSpace, movingMask=brainmask_LG, 
                                    fixed=t1_fMRISpace, fixedMask=brainmask_fmri)

        self.locs_out.CreateDestinationDir()

        self.Log("Moving matrices to " + self.locs_out.dir_subject)
        print(transforms)
        
        os.rename(transforms['invtransforms'][0], self.locs_out.loc_transform_LGToFMRI)


    def GetBrainMask_LGSpace(self):
        
        brainmask = ants.image_read(self.locs_legui.loc_mask_csf)
        brainmask_data = brainmask.numpy()

        brainmask_data = ants.image_read(self.locs_legui.loc_mask_gm).numpy() + brainmask_data
        brainmask_data = ants.image_read(self.locs_legui.loc_mask_csf).numpy() + brainmask_data
        brainmask = brainmask.new_image_like(brainmask_data)
        return brainmask


    def _Register(self, fixed, moving, fixedMask, movingMask):
        self.Log("Registration beginning")
        transform = ants.registration(fixed=fixed, mask=fixedMask, 
                                      moving=moving, moving_mask=movingMask,
                                    type_of_transform="Affine")
        self.Log("Registration completed")
        return transform

    def Log(self, message:str):
        # For extension as needed
        print(message)

if __name__ == "__main__":
    pipeline = LeguiTofMRIPrepRegistrationPipeline("/tmp/lee", "PR03")
    pipeline.Run()