import os
import random
import string
import csv
import cv2
from tqdm import tqdm
from pathlib import Path
import numpy as np


base = os.path.dirname(os.path.realpath(__file__))
imagewidth = 960
imageHight = 540

basedataset = "/home/aitester/Datasets/PFD/"
sorceimagesFoldersList = [  basedataset+file+"/images"  for file in os.listdir(basedataset)  if os.path.isdir(basedataset+file+"/images" )   ]
ground_truth_label_map = [  basedataset+file+"/labels"  for file in os.listdir(basedataset)  if os.path.isdir(basedataset+file+"/labels" )   ]

sorceimagesFoldersList.sort()
ground_truth_label_map.sort()

daatsetName = "PFD"
imageextention = '.png'

save_directory = os.path.join(Path(base).parent.absolute() , "data", daatsetName)
if not os.path.exists(save_directory):
    os.makedirs(save_directory)


save_directoryImages= os.path.join(save_directory, "Images")
if not os.path.exists(save_directoryImages):
    os.makedirs(save_directoryImages)


save_directoryImagesGround_truth= os.path.join(save_directory, "Groundtruth")
if not os.path.exists(save_directoryImagesGround_truth):
    os.makedirs(save_directoryImagesGround_truth)

save_directoryGbuffers= os.path.join(save_directory, "Gbuffers")
if not os.path.exists(save_directoryGbuffers):
    os.makedirs(save_directoryGbuffers)

infodict = {
    "unlabeled": [0, 0, 0, 0],
    "sky": [70, 130, 180, 23],
    "road": [128, 64, 128, 7],
    "static": [20, 20, 20, 8],
    "sidewalk": [244, 35, 232, 9],
    "car": [0, 0, 142, 26],
    "truck": [0, 0, 70, 26],
    "bus": [0, 60, 100, 26],
    "caravan": [0, 0, 90, 26],
    "trailer": [0, 0, 110, 26],
    "train": [0, 80, 100, 26],
    "motorcycle": [0, 0, 230, 26],
    "bicycle": [119, 11, 32, 26],
    "licenseplate": [0, 0, 142, 26],
    "person": [220, 20, 60, 24],
    "rider": [255, 0, 0, 24],
    "Ground": [81, 0, 81, 9],
    "dynamic": [111, 74, 0, 26],
    "building": [70, 70, 70, 4],
    "Wall": [102, 102, 156, 4],
    "Fence": [190, 153, 153, 11],
    "GuardRail": [180, 165, 180, 9],
    "Bridge": [150, 100, 100, 4],
    "tunnel": [150, 120, 90, 4],
    "pole": [153, 153, 153, 17],
    "TrafficLight": [250, 170, 30, 19],
    "TrafficSign": [220, 220, 0, 20],
    "Vegetation": [107, 142, 35, 21],
    "parking": [250, 170, 160, 7],
    "RailTrack": [230, 150, 140, 9],
    "Terrain": [152, 251, 152, 22],
}

def encod_Gt(gt_labelmap):

    h, w, chanel = gt_labelmap.shape
    shader_map = np.zeros((h, w), dtype=np.float32)



    for key in infodict.keys():
        array = infodict.get(key)
        color = np.array(array[:3])
        code=  array[3]

        mask = cv2.inRange(gt_labelmap, color, color)
        shader_map[ np.where(mask ==  255 ) ]  =  code




    return shader_map



allfiles = []

try:

    for index ,folder in enumerate (sorceimagesFoldersList ):

        filelist = list(os.listdir(folder))
        print("\t", folder, "  ->found")
        folder2 = ground_truth_label_map[index]

        for file in tqdm( filelist ):
            path1 = os.path.join(folder , file)
            path2 = os.path.join(folder2 , file)


            try:
                image = cv2.imread(path1)
                image2 = cv2.imread(path2)
                resized_image = cv2.resize(image, (imagewidth, imageHight))
                resized_image2 = cv2.resize(image2, (imagewidth, imageHight))
                resized_image2 = cv2.cvtColor(resized_image2, cv2.COLOR_BGR2RGB)
                encoded_resized_image2 = encod_Gt(resized_image2)

                if file in allfiles:
                    while file in allfiles:
                        file = file + '_'.join(random.choices(string.ascii_uppercase + string.digits, k=5))

                filename = os.path.join(save_directoryImages , file)

                cv2.imwrite(filename, resized_image)
                allfiles.append(file)

                filename = os.path.join(save_directoryImagesGround_truth, file)

                cv2.imwrite(filename, encoded_resized_image2)

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

