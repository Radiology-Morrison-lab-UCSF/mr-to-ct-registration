import subprocess
import SimpleITK as sitk
import os
import shutil
import tempfile
import numpy as np
from PythonUtils.ImageGetter import ImageGetter
from .SkullStripper import SkullStripper
from .IO import WriteImageIfPathProvided
from .Resolution import MMToSimpleITKKernel
import ants

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
        self.loc_mr_brainmask_smoothed = os.path.join(self.dir_output, prefix + "mr_brainmas_smoothed.nii.gz")
        self.loc_ct_brainmask_smoothed = os.path.join(self.dir_output, prefix + "ct_brainmask_smoothed.nii.gz")
        self.loc_mr_skull = os.path.join(self.dir_output, prefix + "mr_skull.nii.gz")
        self.loc_ct_skull = os.path.join(self.dir_output, prefix + "ct_skull.nii.gz")
        self.loc_transform = os.path.join(self.dir_output, prefix + "mr2ct.mat")
        self.loc_mrInCTSpace = os.path.join(self.dir_output, prefix + "mr_inCTSpace.nii.gz")
        self.loc_ctInMRSpace = os.path.join(self.dir_output, prefix + "ct_inMRSpace.nii.gz")


    def Run(self):

        os.makedirs(self.dir_output, exist_ok=True)

        mrBrainMask = SkullStripper(self.mrGetter).CalcBrainmask(self.loc_mr_brainmask)
        ctBrainMask = SkullStripper(self.ctGetter).CalcBrainmask(self.loc_ct_brainmask)

        mrSkullMask = self.ApproximateMRSkull(mrBrainMask)
        ctSkullMask = self.ApproximateCTSkull(ctBrainMask)

        self.SmoothAndRegister(ctSkullMask, mrSkullMask)
        
        self.ApplyTransforms()


    def ApplyTransforms(self):
        loc_mr = self.mrGetter.location
        if loc_mr is None:
            raise Exception("Not implemented - save mr to disk for ants to read")

        loc_ct = self.mrGetter.location
        if loc_ct is None:
            raise Exception("Not implemented - save ct to disk for ants to read")

        self.ApplyTransform(loc_ct, loc_mr, False, self.loc_mrInCTSpace)
        self.ApplyTransform(loc_mr, loc_ct, True, self.loc_ctInMRSpace)


    def ApplyTransform(self, loc_fixed, loc_moving, inverse, loc_saveTo):
        if os.path.exists(loc_saveTo):
           print(loc_saveTo, "found. Transform not applied") 
        else:
            
            transformed = ants.apply_transforms(ants.image_read(loc_fixed), ants.image_read(loc_moving), [self.loc_transform], whichtoinvert=[inverse])
            ants.image_write(transformed, loc_saveTo)


    def SmoothAndRegister(self, fixed:sitk.Image, moving:sitk.Image):
        try:
            if os.path.exists(self.loc_transform):
                print("Transform found. Registration skipped")
                return ants.read_transform(self.loc_transform)
        except:
            print("Transform could not be opened. Rerunning registration")
            pass


        fixedSmoothed = sitk.SmoothingRecursiveGaussian(fixed)
        movingSmoothed = sitk.SmoothingRecursiveGaussian(moving)

        sitk.WriteImage(fixedSmoothed, self.loc_ct_brainmask_smoothed)
        sitk.WriteImage(movingSmoothed, self.loc_mr_brainmask_smoothed)

        return self.Register(self.loc_ct_brainmask_smoothed, self.loc_mr_brainmask_smoothed, self.loc_transform)

        
    def Register(self, loc_fixed:str, loc_moving:str, saveTo:str):
                
        # Generate the transform
        fixed = ants.image_read(loc_fixed)
        moving = ants.image_read(loc_moving)

        print("Running registration")
        transform = ants.registration(fixed=fixed, 
                                        moving=moving, 
                                        type_of_transform="Rigid", 
                                        aff_shrink_factors=(8,6,4,1), 
                                        aff_smoothing_sigmas=(3,2,1,0), 
                                        aff_iterations=(1000,1000,500,100), 
                                        verbose=True)
        print("Registration complete")
        fwdTransform = transform['fwdtransforms'][0]
        shutil.copyfile(fwdTransform, saveTo)
        return fwdTransform
    

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
