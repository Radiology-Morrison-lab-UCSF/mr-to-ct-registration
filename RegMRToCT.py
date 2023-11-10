import subprocess
import SimpleITK as sitk
from ImageGetter import ImageGetter
from SkullStripper import SkullStripper

class RegMRToCTPipeline:

    def __init__(self, mrImgOrLocation, ctImgOrLocation):
        self.mrGetter = ImageGetter(mrImgOrLocation)
        self.ctGetter = ImageGetter(ctImgOrLocation)

    def Run(self):
        mrBrainMask = SkullStripper(self.mrGetter).CalcBrainmask()

        sitk.WriteImage(mrBrainMask, "/home/lreid/temp/temp.nii.gz", useCompression=True, imageIO="NiftiImageIO")

        #ctBrainMask = self.ApproximateCTBrainMask()

        #sitk.WriteImage(ctBrainMask, "/home/lreid/temp/temp.nii.gz", useCompression=True, imageIO="NiftiImageIO")

        raise Exception("Incomplete")
    
    


    def ApproximateCTBrainMask(self) -> sitk.Image:
        # Houndsfield units for a CT:
        # GM: 37 - 45
        # WM: 20 - 30
        # Water: 0
        # Bone: 700 - 3000
        # The artefacts we see have very large numbers, usually

        # Find tissues, roughly
        ct = self.ctGetter.GetImage()
        ct_downsampled = self.Resample(ct, [int(x/4) for x in ct.GetSize()])


        ct_GmWm = (ct_downsampled > 20) * (ct_downsampled < 45)
        ct_water = ct_downsampled == 0
        ct_skull = (ct_downsampled >= 700) * (ct_downsampled < 2000)

        # # fill the skull
        # roughhead = ct_skull
        # #roughhead = sitk.BinaryErode(roughhead, kernelRadius=[2,2,2])
        # for i in range(20):
        #     print(i)
        #     #roughhead = f.Execute(roughhead)
        #     roughhead = sitk.BinaryErode(sitk.BinaryDilate(roughhead, kernelRadius=[10,10,10]), kernelRadius=[10,10,10])
        #     sitk.WriteImage(roughhead, "/home/lreid/temp/roughhead"+str(i)+".nii.gz", useCompression=True, imageIO="NiftiImageIO")


        # Keep gm/wm and water within the GM/WM areas
        kernel = [1,1,1]
        roughBrain = sitk.BinaryDilate(ct_GmWm, kernelRadius=[3,3,3])
        roughBrain = ct_water * roughBrain + ct_GmWm
        roughBrain = sitk.BinaryDilate(sitk.BinaryErode(roughBrain, kernelRadius=kernel), kernelRadius=kernel) # remove 1-voxel bits 
        kernel = [3,3,3]
        for i in range(10):
            roughBrain = sitk.BinaryErode(sitk.BinaryDilate(roughBrain, kernelRadius=kernel), kernelRadius=kernel) # join bits

        

        sitk.WriteImage(roughBrain, "/home/lreid/temp/roughbrain.nii.gz", useCompression=True, imageIO="NiftiImageIO")


        # Find islands
        f = sitk.ConnectedComponentImageFilter()
        islands = f.Execute(roughBrain)
        objCount = f.GetObjectCount()

        sitk.WriteImage(islands, "/home/lreid/temp/islands.nii.gz", useCompression=True, imageIO="NiftiImageIO")

        # Keep the biggest one
        maxSize = 0
        maxLabel = -1
        print("Found: ", objCount+1)
        for labl in range(1,objCount+1):
            filt = sitk.StatisticsImageFilter()
            filt.Execute(islands == labl)
            voxCount = filt.GetSum()
            print(labl, " size: ", voxCount)

            if voxCount > maxSize:
                maxLabel = labl
                maxSize = voxCount

        finalDownsampled = islands == maxLabel
        return self.Resample(finalDownsampled, ct.GetSize())


    def Resample(self, img:sitk.Image, new_size) -> sitk.Image:
        # The spatial definition of the images we want to use in a deep learning framework (smaller than the original).
        
        reference_image = sitk.Image(new_size, img.GetPixelIDValue())
        reference_image.SetOrigin(img.GetOrigin())
        reference_image.SetDirection(img.GetDirection())
        reference_image.SetSpacing(
            [
                sz * spc / nsz
                for nsz, sz, spc in zip(new_size, img.GetSize(), img.GetSpacing())
            ]
        )

        return sitk.Resample(img, reference_image)



pipeline = RegMRToCTPipeline("/home/lreid/temp/MR.nii", "/home/lreid/temp/CT.nii")
pipeline.Run()