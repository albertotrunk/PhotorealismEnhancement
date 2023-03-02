import os
import random
import string
import csv
import cv2
from tqdm import tqdm
from pathlib import Path

base = os.path.dirname(os.path.realpath(__file__))
imagewidth = 960
imageHight = 540

basedataset = "/home/aitester/Datasets/camera_lidar_semantic/"

sorceimagesFoldersList = [  basedataset+file+"/camera/cam_front_center"  for file in os.listdir(basedataset)  if os.path.isdir(basedataset+file+"/camera/cam_front_center" )  ]

print(sorceimagesFoldersList)


daatsetName = "A2d2"


save_directory = os.path.join(Path(base).parent.absolute() , "data", daatsetName)
if not os.path.exists(save_directory):
    os.makedirs(save_directory)


save_directoryImages= os.path.join(save_directory, "Images")
if not os.path.exists(save_directoryImages):
    os.makedirs(save_directoryImages)





allfiles = []



for folder in sorceimagesFoldersList:
    print(folder)
    try:
        filelist = list(os.listdir(folder))
        print("\t", folder, "  ->found")
        for file in tqdm( filelist ):
            path1 = os.path.join(folder , file)

            try:
                image = cv2.imread(path1)
                resized_image = cv2.resize(image, (imagewidth, imageHight))
                if file in allfiles:
                    while file in allfiles:
                        file = file + '_'.join(random.choices(string.ascii_uppercase + string.digits, k=5))

                filename = os.path.join(save_directoryImages , file)

                cv2.imwrite(filename, resized_image)
                allfiles.append(file)

            except:
                print(path1," is not loadabel as image")

    except:
        print("no files was resized")

save_filelist = list(os.listdir(save_directoryImages))

with open(os.path.join(save_directory, f"{daatsetName}.csv"), 'w') as f:
    # create the csv writer
    writer = csv.writer(f)

    for file in tqdm( save_filelist ):
        path = os.path.join(save_directoryImages, file)
        try:
            image = cv2.imread(path)
            writer.writerow([path])
        except:
            print(path, " is not loadabel as image")

