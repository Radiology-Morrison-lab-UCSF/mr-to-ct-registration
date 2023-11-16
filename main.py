from MRToCT import RegMRToCT

pipeline = RegMRToCT.RegMRToCTPipeline("/data/morrison/wip/lee/legui_julian/sub-rcs02_ses-01_desc-preproc_T1w.nii.gz",
                                       "/data/morrison/wip/lee/legui_julian/CT.nii.gz", 
                                       "/data/morrison/wip/lee/legui_julian/")
pipeline.Run()