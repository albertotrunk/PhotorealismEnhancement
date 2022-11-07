'''
Created on 05.07.2022

@author: rizka
'''

import cv2
import numpy as np
import glob, os
from tqdm import tqdm

if __name__ == '__main__':

    base = os.path.dirname(os.path.realpath(__file__))
    #ImageExtention = "jpg"

    Output = "/home/aitester/PycharmProjects/PhotorealismEnhancement/code/out/Carla2A2d2"#"CarlaOut"
    Input  = "/home/aitester/PycharmProjects/PhotorealismEnhancement/data/Carla/Images"#"sourceCalraA"



    width = 960
    height = 540
    dim = (width, height)



    imagefilelist = []

    os.chdir(Output)
    for file in glob.glob("*.jpg"):
        #print(file)
        Imagekey = file.replace(f".jpg", "")
        print(Imagekey)
        imagefilelist.append(Imagekey )

    imagefilelist.sort()
    imagefilelist.sort()

    imagelist = []



    Videoheight, Videowidth  =   height , width*2
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    video = cv2.VideoWriter(os.path.join(base, 'video.avi'), fourcc, 30, (Videowidth, Videoheight))
    print("video.write")

    for Imagekey in tqdm(imagefilelist ):

        inputpath = os.path.join(Input, Imagekey + f'.png')
        outputpath =  os.path.join(Output , Imagekey + f'.jpg')


        if os.path.isfile(inputpath) and os.path.isfile(outputpath):
            try:
                InputImage = cv2.imread(inputpath)
                OutputImage = cv2.imread(outputpath)

                InputImage = cv2.resize(InputImage, dim, interpolation=cv2.INTER_LANCZOS4)
                OutputImage = cv2.resize(OutputImage, dim, interpolation=cv2.INTER_LANCZOS4)


                imgobj = np.concatenate((InputImage,OutputImage), axis=1)
                video.write(imgobj)


            except:
                print(Imagekey , "-->has an error")




    cv2.destroyAllWindows()
    video.release()