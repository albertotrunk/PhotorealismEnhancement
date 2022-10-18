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
infodict[ "sky"  ]  = [128,128,128, 23   ]
infodict[ "road"  ]  = [128,64,128, 7  ]
infodict[ "static"  ]  = [128,128,192, 8   ]
infodict[ "sidewalk"  ]  = [0,0,192  , 9   ]
infodict[ "vehicle"  ]  = [64,0,128 , 26   ]

infodict[ "Truck_Bus"  ]  = [192,128,192, 26   ]
infodict[ "SUVPickupTruck"  ]  = [64,128,192, 26   ]

infodict[ "MotorcycleScooter"  ]  = [192,0,192, 26   ]

infodict[ "unlabeled"  ]  = [0, 0, 0, 0   ]

infodict[ "building"  ]  = [128,0,0 , 4  ]
infodict["Fence"] = [64,64,128,  11 ]

infodict["other"] = [128,64,64,  0 ]

infodict["Pedestrian"] = [64,64,0  , 24  ]

infodict["infrastructure"] = [192,192,128 , 17 ]

infodict["RoadLine"] = [128,0,192 , 7]

infodict["Vegetation"] = [192,192,0  ,  21 ]
infodict["Tree"] = [128,128,0  ,  21 ]

infodict["Wall"] = [64,192,0 ,  4  ]

infodict["TrafficSign"] = [192,128,128 , 20]
infodict["Misc_Text"] = [128,128,6, 20]


infodict["Ground"] = [192,192,0 , 9]

infodict["Bridge"] = [0,128,64 ,  4  ]

infodict["RailTrack"] = [64,0,192 , 9  ]

infodict["GuardRail"] = [192,0,64 , 9  ]
infodict["TrafficCone"] = [0,0,64 , 9  ]
infodict["ParkingBlock"] = [64,192,128, 9  ]


infodict["TrafficLight"] = [0,64,64 , 19  ]

infodict["Terrain"] = [192,64,128, 22 ]
 

infodict["Animal"] = [64,128,64 , 24  ]
infodict["Child"] = [192,128,64  , 24  ]
infodict["Bicyclist"] = [0,128,192 , 24  ]


infodict[ "Archway"  ]  = [64,128,64, 4  ]
infodict[ "Tunnel"  ]  = [64,0,64, 4  ]

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

