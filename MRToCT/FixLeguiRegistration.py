import PythonUtils.HDF5
from PythonUtils.IO import WriteTextFile
from PythonUtils.ImageGetter import ImageGetter
from PythonUtils.OSUtils import AllExist, GetFilename
import ants
import numpy as np
import os
import shutil
import tempfile
from .LeGuiFileLocations import LeGuiFileLocations
from .RegisterMRToCTPipeline import RegisterMRToCTPipeline


class FixLeguiRegistration:

    def __init__(self, mrImgOrLocation, dir_legui, dir_output, prefix = "", useGPU=False):
        self.locs_legui = LeGuiFileLocations(os.path.abspath(dir_legui))
        self.mrGetter = ImageGetter(mrImgOrLocation)
        self.ctGetter = ImageGetter(self.locs_legui.loc_CT)
        self.dir_output = os.path.abspath(dir_output)
        self.mr_InCTSpace = os.path.join(self.dir_output, prefix + "mr_in_ct_space.nii.gz")
        self.ct_InMRSpace = os.path.join(self.dir_output, prefix + "ct_in_mr_space.nii.gz")
        self.transform_MRToCT = os.path.join(self.dir_output, prefix + "mr_to_ct.mat")
        self.keepIntermediates = False
        self.useGPU = useGPU
        self.prefix = prefix


    def Run(self):
        self.locs_legui.AssertCTFound()
        self.locs_legui.AssertElectrodesFound()

        os.makedirs(self.dir_output, exist_ok=True)

        self.RegisterMRToCT()
        transform = ants.read_transform(self.transform_MRToCT)
        self.TransformCoords(transform, "ElecXYZRaw")
        self.TransformCoords(transform, "ElecXYZProjRaw")
        self.WriteReadme()

    def WriteReadme(self):
        saveTo = os.path.join(self.dir_output, self.prefix + "README.txt")

        readme = 'Files reflect a new rigid registration between the LeGUI CT (' +\
        self.ctGetter.location + ') and MR image at ' + self.mrGetter.location + '.\n' +\
        'This MR is NOT in the same space as the MR appearing in the LeGUI directory: the MR appearing in the LeGUI directory is unlikely to be well aligned with the CT, and is potentially left-right flipped.\n' +\
        '\n' +\
        'Files\n' +\
        '-----\n' +\
        GetFilename(self.mr_InCTSpace) + ':\tThe MR image transformed into CT space\n' +\
        GetFilename(self.ct_InMRSpace) + ':\tThe CT image transformed into MR space\n' +\
        GetFilename(self.transform_MRToCT) + ":\tThe rigid transform from MR to CT. Ants (ITK) format. Note the direction is MR->CT.\n" +\
        "Other .txt files:\tCoordinates from Electrodes.mat transformed into MR space (RAS, patient space), in the same order they appear in that .mat file\n"

        WriteTextFile(saveTo, readme)



    def TransformCoords(self, transform, field):

        loc_saveTo = os.path.join(self.dir_output, self.prefix + field + "_in_mr_space.txt")

        if os.path.exists(loc_saveTo):
            print(loc_saveTo, "exists. Calculation skipped.")
            return

        coordinates = PythonUtils.HDF5.ReadMatFileArray(self.locs_legui.loc_electrodes, field)

        # Convert RAS to LPS for ITK
        coordinates[:,0] *= -1
        coordinates[:,1] *= -1

        newCoords = np.array([transform.apply_to_point(c) for c in coordinates])

        # Then back to RAS
        newCoords[:,0] *= -1
        newCoords[:,1] *= -1

        np.savetxt(loc_saveTo, newCoords, delimiter='\t', newline='\n')



    def RegisterMRToCT(self):
        if AllExist([self.ct_InMRSpace, self.mr_InCTSpace, self.transform_MRToCT]):
            print("Pre-existing registration found. Recalculation not performed.")
            return

        # Register and keep only the files we want
        # We work in a temporary directory to avoid file clashes
        tempDir = self.dir_output if self.keepIntermediates else tempfile.mkdtemp()
        try:
            pipeline = RegisterMRToCTPipeline(self.mrGetter, self.ctGetter, tempDir, prefix="", useGPU = self.useGPU)
            pipeline.Run()
            shutil.move(pipeline.loc_mrInCTSpace, self.mr_InCTSpace)
            shutil.move(pipeline.loc_ctInMRSpace, self.ct_InMRSpace)
            shutil.move(pipeline.loc_transform, self.transform_MRToCT)
        finally:
            # Clean up
            if not self.keepIntermediates:
                shutil.rmtree(tempDir)