import imagehash
import cv2
from PIL import Image
import os
import imagehash
arrayprueba=[]
from difflib import SequenceMatcher
a=2
b=1
path = r'C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\Be4'
pathB = r'C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After'
os.chdir(path)
hashA=imagehash.phash(Image.open(f'frames_0{a}_0{b}.png'))
os.chdir(pathB)
hashB=imagehash.phash(Image.open(f'frames_0{a}_0{b}.png'))

asd=(str(hashA))
bas=(str(hashB))


def similar(a,b):  
    return SequenceMatcher(None,a,b).ratio()

print(similar(asd,bas))
