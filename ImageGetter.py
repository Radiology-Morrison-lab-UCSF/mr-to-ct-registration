import SimpleITK as sitk

class ImageGetter:

    def __init__(self, locationOrImage):
        if type(locationOrImage) is str:
            self.location = locationOrImage
            self.cached = None
        else:
            self.location = None
            self.cached = locationOrImage


    def GetImage(self):
        '''
        Returns an image from file
        '''

        self.CacheImage()

        return self.cached

    def CacheImage(self):
        self.cached = sitk.ReadImage(self.location, imageIO="NiftiImageIO")


def GetImage(locationOrImage):
    return ImageGetter(locationOrImage).GetImage()