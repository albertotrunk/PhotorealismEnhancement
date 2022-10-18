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

infodict = dict()
infodict[ "sky"  ]  = [70, 130, 180, 23   ]
infodict[ "road"  ]  = [128, 64, 128, 7  ]
infodict[ "static"  ]  = [110, 190, 160, 8   ]
infodict[ "sidewalk"  ]  = [244, 35, 232 , 9   ]
infodict[ "vehicle"  ]  = [0, 0, 142 , 26   ]
infodict[ "unlabeled"  ]  = [0, 0, 0, 0   ]
infodict[ "building"  ]  = [70, 70, 70 , 4  ]
infodict["Fence"] = [100, 40, 40 ,  11 ]
infodict["other"] = [55, 90, 80 ,  0 ]
infodict["Pedestrian"] = [220, 20, 60 , 24  ]
infodict["infrastructure"] = [153, 153, 153 , 17 ]
infodict["RoadLine"] = [157, 234, 50 , 7]
infodict["Vegetation"] = [107, 142, 35 ,  21 ]
infodict["Wall"] = [102, 102, 156 ,  4  ]
infodict["TrafficSign"] = [220, 220, 0 , 20]
infodict["Ground"] = [81, 0, 81 , 9]
infodict["Bridge"] = [150, 100, 100 ,  4  ]
infodict["RailTrack"] = [230, 150, 140 , 9  ]
infodict["GuardRail"] = [180, 165, 180 , 9  ]
infodict["TrafficLight"] = [250, 170, 30 , 19  ]
infodict["Terrain"] = [145, 170, 100 , 22 ]


def encod_Gt(gt_labelmap):

        h, w, chanel = gt_labelmap.shape
        shader_map = np.zeros((h, w), dtype=np.float32)



        for key in infodict.keys():
            array = infodict.get(key)
            color = np.array(array[ 0:3])
            code=  array[3]

            mask = cv2.inRange(gt_labelmap, color, color)
            shader_map[ np.where(mask ==  255 ) ]  =  code




        return shader_map



allfiles = []

try:

    for index ,folder in enumerate (sorceimagesFoldersList ) :

        filelist = [file for file in os.listdir(folder)   ]
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

save_filelist = [file for file in os.listdir(save_directoryImages)   ]

f = open( os.path.join(save_directory , daatsetName + ".csv"), 'w')
# create the csv writer
writer = csv.writer(f)

for file in tqdm( save_filelist ):
    path = os.path.join(save_directoryImages, file)
    try:
        image = cv2.imread(path)
        writer.writerow([path])
    except:
        print(path, " is not loadabel as image")

# close the file
f.close()

