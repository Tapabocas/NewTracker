#guarda las imagenes en A y les asigna un hash. el hash se convierte a tipo string y se guarda en el array hashmatrix.
def main():
  import cv2
  import numpy as np
  import image_slicer
  import imagehash
  from PIL import Image
  import os
  import time
  import threading
  import shutil

  hashmatrix=[]
  path = r'C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\Be4'
  
  os.chdir(path)
  count=0
  #while True:
  captura = cv2.VideoCapture(0)
  while (captura.isOpened()):
    ret, imagen = captura.read()
    if ret:
      #cv2.imshow('video', imagen)   #no necesito ver la imagen completa, but la imagen compuesta de las pieces.
      time.sleep(0.5)
      #cv2. imwrite(os.path.join(path , "frames.jpg" , imagen))
      cv2.imwrite("frames.jpg" , imagen)
      captura.set(1, count)
      imagenesPartidas=image_slicer.slice("frames.jpg",16)
      time.sleep(0.5)
      for i in range (1,5):
        for j in range (1,5):
        
          a=f'frames_0{i}_0{j}.png'
          #    
          b=f'C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After\\frames_0{i}_0{j}.png'
          shutil.copy(a,b)


      print(type(imagenesPartidas))
      print(len(imagenesPartidas))
      for i in range (1,5):
        for j in range (1,5):
          hash=imagehash.average_hash(Image.open(f'frames_0{i}_0{j}.png'))
          #hashmatrix.append(hash)
          #print(hashmatrix)
          #print (i)
          #print (j)
          hashmatrix.append(str(hash))
      if i==j==4:
        print(hashmatrix)
        
        
    else:              
      continue

    #time.sleep(2)

    #time.sleep(2)
    hashmatrix.clear()
#hash=imagehash.average_hash(Image.open(f'frames_01_01.png'))
#print(hash)
   




if __name__=='__main__':
    main()
    time.sleep(2)
    

