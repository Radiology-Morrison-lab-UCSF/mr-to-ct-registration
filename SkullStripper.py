import RunHDBet
from ImageGetter import ImageGetter
from InstallPaths import InstallPaths


import SimpleITK as sitk


import os
import tempfile


class SkullStripper:
    def __init__(self, mrImgOrLocation):
        self.mrGetter = ImageGetter(mrImgOrLocation)
        

    def CalcBrainmask(self)  -> sitk.Image:
        '''
        Returns a mask of the brain
        '''


        loc_in = self.mrGetter.location
        writeAndDelete = loc_in is None
        if writeAndDelete:
            loc_in = tempfile.mktemp(suffix="nii")
            sitk.WriteImage(self.mrGetter.GetImage(), loc_in)

        loc_out = tempfile.mktemp(suffix="nii")
        RunHDBet.RunHDBet_CPU(loc_in, loc_out)

        img = sitk.ReadImage(loc_out)

        # Cleanup
        os.remove(loc_out)
        if writeAndDelete:
            os.remove(loc_in)

        return img