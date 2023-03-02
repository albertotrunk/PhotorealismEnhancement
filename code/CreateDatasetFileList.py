import os
import random
import string
import csv
import cv2
from tqdm import tqdm
from pathlib import Path
import numpy as np


base = Path (os.path.dirname(os.path.realpath(__file__)))

print(base)

#daatsetName = "Carla"
imageextention = '.png'

for daatsetName in ["Carla"]:#["PFD"  ,"A2d2"  ]:

    save_directory = Path(os.path.join(Path(base).parent , "data", daatsetName) )
    print(save_directory)
    save_directoryImages=  save_directory.joinpath( "Images")
    print(save_directoryImages)
    save_directoryImagesGroundtruth =  save_directory.joinpath("Groundtruth")
    save_directoryGbuffers= save_directory.joinpath("Gbuffers")
    save_directoryGray=  save_directory.joinpath("gray")



    save_filelist = list(os.listdir(save_directoryImages))



    with open(os.path.join(save_directory, f"{daatsetName}.txt"), 'w') as text_file:


        for file in tqdm( save_filelist ):
            pathImage =  save_directoryImages.joinpath( file)
            pathImageGroundtruth =  save_directoryImagesGroundtruth.joinpath( file)
            pathGray =  save_directoryGray.joinpath( file)
            pathGbuffers = save_directoryGbuffers.joinpath(f"{Path(file).stem}.npz")

            if save_directoryGbuffers.exists():
                try:
                    image = cv2.imread(str(pathImage))
                    image2 = cv2.imread(str(pathGray))
                    image3 = cv2.imread(str(pathImageGroundtruth))
                    data = np.load(str(pathGbuffers))
                    if pathImage.exists() and  pathGray.exists() and pathImageGroundtruth.exists() and  pathGbuffers.exists():
                        text_file.write(
                            f"{str(pathImage)},{str(pathGray)},{str(pathGbuffers)},{str(pathImageGroundtruth)}"
                            + ",\n"
                        )

                    else:
                        print("Why")
                        print(pathImage.absolute())
                        print(pathGray.absolute())

                except:
                    print(pathImage, " is not loadabel as image")
            else:
                try:
                    image = cv2.imread(str(pathImage))
                    image2 = cv2.imread(str(pathGray))
                    if pathImage.exists() and  pathGray.exists():
                        text_file.write(f"{str(pathImage)},{str(pathGray)}" + ",\n")

                except:
                    print(pathImage, " is not loadabel as image")


