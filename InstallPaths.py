import os


class InstallPaths:
    def __init__(self):
        self.dir_top = os.path.realpath(__file__)
        self.dir_hdbet = os.path.join(self.dir_top,"HD_BET/")
        self.hdbet = os.path.join(self.dir_hdbet,"HD_BET", "hd-bet")