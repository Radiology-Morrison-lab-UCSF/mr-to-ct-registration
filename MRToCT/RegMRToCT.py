import subprocess
import SimpleITK as sitk
import os
import numpy as np
from .ImageGetter import ImageGetter
from .SkullStripper import SkullStripper
from .IO import WriteImageIfPathProvided
from .Resolution import MMToSimpleITKKernel

class RegMRToCTPipeline:

    def __init__(self, mrImgOrLocation, ctImgOrLocation, dir_output, prefix = "mr_to_ct_"):
        '''
        
        :mrImgOrLocation: Should point to a T1. Supply a string, Image, or ImageGetter
        '''
        self.mrGetter = ImageGetter(mrImgOrLocation)
        self.ctGetter = ImageGetter(ctImgOrLocation)
        self.dir_output = dir_output
        self.loc_mr_brainmask = os.path.join(self.dir_output, prefix + "mr_brainmask.nii.gz")
        self.loc_ct_brainmask = os.path.join(self.dir_output, prefix + "ct_brainmask.nii.gz")
        self.loc_mr_skull = os.path.join(self.dir_output, prefix + "mr_skull.nii.gz")
        self.loc_ct_skull = os.path.join(self.dir_output, prefix + "ct_skull.nii.gz")

    def Run(self):

        os.makedirs(self.dir_output, exist_ok=True)

        mrBrainMask = SkullStripper(self.mrGetter).CalcBrainmask(self.loc_mr_brainmask)
        ctBrainMask = SkullStripper(self.ctGetter).CalcBrainmask(self.loc_ct_brainmask)

        mrSkullMask = self.ApproximateMRSkull(mrBrainMask)
        ctSkullMask = self.ApproximateCTSkull(ctBrainMask)


        raise Exception("Incomplete - run registration between skulls")
    

    def ApproximateMRSkull(self, mrBrainMask:sitk.Image):
        '''
        Approximates and saves the MR skull, if it is not already found on disk
        '''

        if os.path.exists(self.loc_mr_skull):
            skullMask = sitk.ReadImage(self.loc_mr_skull)
        else:
            # The skull is up to 1cm thick
            # The dura is about 1mm, arachnoid less thick (I think)
            kernSize = MMToSimpleITKKernel(mrBrainMask, 12)
            skullAndScalpMask = sitk.BinaryDilate(mrBrainMask, kernelRadius=kernSize) - mrBrainMask

            t1 = self.mrGetter.GetImage()

            # The scalp is very bright, the skull looks like air
            threshold = self.GetMeanInMask(t1,skullAndScalpMask)
            skullMask = (t1 < threshold) * skullAndScalpMask

            WriteImageIfPathProvided(skullMask, self.loc_mr_skull)
        return skullMask
    

    def GetMin(self, image:sitk.Image) -> float:
        return sitk.GetArrayViewFromImage(image).min()
    
    def GetMean(self, image:sitk.Image) -> float:
        return sitk.GetArrayViewFromImage(image).mean()

    def GetMeanInMask(self, image:sitk.Image, mask:sitk.Image):
        masked = sitk.Mask(image, mask)
        
        maskValues = sitk.GetArrayViewFromImage(mask)
        values = sitk.GetArrayViewFromImage(masked)
        return np.sum(values) / np.count_nonzero(maskValues)



    def ApproximateCTSkull(self, ctBrainMask:sitk.Image):
        '''
        Approximates and saves the CT skull, if it is not already found on disk
        '''
        if os.path.exists(self.loc_ct_skull):
            skull = sitk.ReadImage(self.loc_ct_skull)
        else:
            halfKernel = MMToSimpleITKKernel(ctBrainMask, 2.5)
            kernel_5mm = MMToSimpleITKKernel(ctBrainMask, 5)
            kernel_25mm = MMToSimpleITKKernel(ctBrainMask, 25)
            

            # Look quite widely around the brain, and inside it too as the brainmask can be overzealous
            ctBrainMask_shrunk = sitk.BinaryErode(ctBrainMask,kernelRadius=kernel_5mm)
            skull = sitk.BinaryDilate(ctBrainMask_shrunk, kernelRadius=kernel_25mm) - ctBrainMask_shrunk

            # ... But then restrict to plausible intensities
            # Houndsfield units for a CT:
            # GM: 37 - 45
            # WM: 20 - 30
            # Water: 0
            # Bone: 700 - 3000
            # The artefacts we see have very large numbers, usually, but can be bone-like

            ct = self.ctGetter.GetImage()
            boneLike = (ct >= 700) * (ct < 2000) 

            # Eliminate aliasing near electrode leads
            # -- Remove anything near something electrode like
            bone_noElectrodes = boneLike * sitk.BinaryErode(ct < 2700, kernel_5mm)
            # -- Close holes in the skull caused by electrodes passing through
            bone_noElectrodes = sitk.BinaryDilate(bone_noElectrodes, kernelRadius=halfKernel) * boneLike

            skull *= bone_noElectrodes

            WriteImageIfPathProvided(skull, self.loc_ct_skull)
        return skull


    # def ApproximateCTBrainMask(self) -> sitk.Image:
    #     # Houndsfield units for a CT:
    #     # GM: 37 - 45
    #     # WM: 20 - 30
    #     # Water: 0
    #     # Bone: 700 - 3000
    #     # The artefacts we see have very large numbers, usually

    #     # Find tissues, roughly
    #     ct = self.ctGetter.GetImage()
    #     ct_downsampled = self.Resample(ct, [int(x/4) for x in ct.GetSize()])


    #     ct_GmWm = (ct_downsampled > 20) * (ct_downsampled < 45)
    #     ct_water = ct_downsampled == 0
    #     ct_skull = (ct_downsampled >= 700) * (ct_downsampled < 2000)


    #     # # fill the skull
    #     # roughhead = ct_skull
    #     # #roughhead = sitk.BinaryErode(roughhead, kernelRadius=[2,2,2])
    #     # for i in range(20):
    #     #     print(i)
    #     #     #roughhead = f.Execute(roughhead)
    #     #     roughhead = sitk.BinaryErode(sitk.BinaryDilate(roughhead, kernelRadius=[10,10,10]), kernelRadius=[10,10,10])
    #     #     sitk.WriteImage(roughhead, "/home/lreid/temp/roughhead"+str(i)+".nii.gz", useCompression=True, imageIO="NiftiImageIO")


    #     # Keep gm/wm and water within the GM/WM areas
    #     kernel = [1,1,1]
    #     roughBrain = sitk.BinaryDilate(ct_GmWm, kernelRadius=[3,3,3])
    #     roughBrain = ct_water * roughBrain + ct_GmWm
    #     roughBrain = sitk.BinaryDilate(sitk.BinaryErode(roughBrain, kernelRadius=kernel), kernelRadius=kernel) # remove 1-voxel bits 
    #     kernel = [3,3,3]
    #     for i in range(10):
    #         roughBrain = sitk.BinaryErode(sitk.BinaryDilate(roughBrain, kernelRadius=kernel), kernelRadius=kernel) # join bits

        

    #     sitk.WriteImage(roughBrain, "/home/lreid/temp/roughbrain.nii.gz", useCompression=True, imageIO="NiftiImageIO")


    #     # Find islands
    #     f = sitk.ConnectedComponentImageFilter()
    #     islands = f.Execute(roughBrain)
    #     objCount = f.GetObjectCount()

    #     sitk.WriteImage(islands, "/home/lreid/temp/islands.nii.gz", useCompression=True, imageIO="NiftiImageIO")

    #     # Keep the biggest one
    #     maxSize = 0
    #     maxLabel = -1
    #     print("Found: ", objCount+1)
    #     for labl in range(1,objCount+1):
    #         filt = sitk.StatisticsImageFilter()
    #         filt.Execute(islands == labl)
    #         voxCount = filt.GetSum()
    #         print(labl, " size: ", voxCount)

    #         if voxCount > maxSize:
    #             maxLabel = labl
    #             maxSize = voxCount

    #     finalDownsampled = islands == maxLabel
    #     return self.Resample(finalDownsampled, ct.GetSize())
    # def Resample(self, img:sitk.Image, new_size) -> sitk.Image:
    #     # The spatial definition of the images we want to use in a deep learning framework (smaller than the original).
        
    #     reference_image = sitk.Image(new_size, img.GetPixelIDValue())
    #     reference_image.SetOrigin(img.GetOrigin())
    #     reference_image.SetDirection(img.GetDirection())
    #     reference_image.SetSpacing(
    #         [
    #             sz * spc / nsz
    #             for nsz, sz, spc in zip(new_size, img.GetSize(), img.GetSpacing())
    #         ]
    #     )

    #     return sitk.Resample(img, reference_image)



pipeline = RegMRToCTPipeline("/home/lreid/temp/MR.nii", "/home/lreid/temp/CT.nii", "/home/lreid/temp/reg/")
pipeline.Run()