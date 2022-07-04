#asno
import cv2
import os
from datetime import datetime
import image_slicer
import threading
import time
import shutil
import imagehash
from PIL import Image

path = r'C:\Users\Camilo Palacios\Desktop\A'
 

os.chdir(path)


wait = 0
 

video = cv2.VideoCapture(0)

 
#def generate():

while True:
    ret, img = video.read()

    
    cv2.imwrite('generadas.jpg', img)
    imagenesPartidas=image_slicer.slice("generadas.jpg",16)
    #time.sleep(2)

    video.release()

    cv2.destroyAllWindows()

#def compare():
#    for i in range (1,5):
#        for j in range (1,5):
#            if f'C:\\Users\\Camilo Palacios\\Desktop\A\\filename_0{i}_0{j}.png'==f'C:\\Users\\Camilo Palacios\\Desktop\\B\\frames_0{i}_0{j}.png':
#                print('Iguales')
#            else:
#                print("Diferentes")


#def save():
#    time.sleep(1)
#    for i in range (1,5):
#        for j in range (1,5):
#            a=f'generadas_0{i}_0{j}.png'
#            b=f'C:\\Users\\Camilo Palacios\\Desktop\\B\\frames_0{i}_0{j}.png'
#            shutil.copy(a,b)

