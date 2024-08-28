import numpy as np
import SimpleITK as sitk
from typing import List

def MMToSimpleITKKernel(image:sitk.Image, mm:float) -> List[float]:
    '''
    Converts MM into XYZ measurements compatible with simple ITK's kernels
    '''
    return np.round(MMToVoxelsXYZ(image, mm)).astype(np.int32).tolist()


def MMToVoxelsXYZ(image:sitk.Image, mm:float) -> np.array:
    '''
    Converts MM to voxels in each dimension
    '''
    resolution = image.GetSpacing()
    return mm / np.array(resolution)

