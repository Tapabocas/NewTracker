#guarda las imagenes en A y les asigna un hash. el hash se convierte a tipo string y se guarda en el array hashmatrix.

import cv2
import numpy as np
import image_slicer
import imagehash
from PIL import Image
import os
import time
import threading
import shutil
def main():
  #tiempo=2
  hashmatrixA=[]
  hashmatrixB=[]
  path = r'C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\Be4'





  def paso1():
    
    os.chdir(path)
    captura = cv2.VideoCapture(0)
    while (captura.isOpened()):
      ret, imagen = captura.read()
      if ret:
        cv2.imwrite("frames.jpg" , imagen)
        image_slicer.slice("frames.jpg",16)
        for i in range (1,5):
          for j in range (1,5):
            hashA=imagehash.average_hash(Image.open(f'frames_0{i}_0{j}.png'))
            hashmatrixA.append(str(hashA))
        if i==j==4:
          print(hashmatrixA)
          hashmatrixA.clear() 
          time.sleep(8)
          paso2()
          
          
        else:              
          continue

  def paso2():
    for i in range (1,5):
      for j in range (1,5):
        a=f'frames_0{i}_0{j}.png'
        b=f'C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After\\frames_0{i}_0{j}.png'
        shutil.copy(a,b)
    os.chdir(r'C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After')
    for i in range (1,5):
      for j in range (1,5):    
        os.chdir(r'C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After')
        hashB=imagehash.average_hash(Image.open(f'frames_0{i}_0{j}.png'))
        hashmatrixB.append(str(hashB))
    
    if j==i==4:
      print(hashmatrixB)
      hashmatrixB.clear()
      os.chdir(path)

  paso1()

  #def paso3():

    #En realidad es el paso 2, pero continuemos
    #Sacar hash solamente a las miágenes de la carpeta B. (En el paso 2) , para que un array de hashes generado junto con las imagenes en A, se borre cada vez y se *compare*.
   # print("Si.")
    #para compararlos, aquí se traen ambos arreglos y se comparan elemento por elemento.. dependiendo de cuales sean disitntos, se encierra o no.
    #for i in range (1,16):
     #   if hashmatrixA(i)==hashmatrixB(i):
      #    print("Son iguales")
       # else:
        #  print("Son re diferentes")
          


  #thread=threading.Thread(target=paso1)
  #thread.start() 
  #thread2=threading.Thread(target=paso2)
  #thread2.start() 
  #thread3=threading.Thread(target=paso3)
  #thread3.start() 


if __name__=='__main__':
    
    print("Si, si ..")
    #time.sleep(2)
    print("Si, si ..again")
    main()
    print("Y esto?")


