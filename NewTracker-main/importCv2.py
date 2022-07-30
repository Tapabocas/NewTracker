#guarda las imagenes en A y les asigna un hash. el hash se convierte a tipo string y se guarda en el array hashmatrix.
# what if saco el hash DESPUÉS de que las imagenes sean distintas..  . . . ...............
import cv2
import numpy as np
import image_slicer
import imagehash
from PIL import Image
import os
import time
import threading
import shutil

hashmatrixA=[]
#hashmatrixB=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p']
hashmatrixB=[]
def main():

  #path = r'D:\\Desktop\\NewTracker-Funciona_Sin_Threads\\Be4'
  path = r'C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\Be4'



  def paso1():
    print("Inicio del paso 1")
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
      
        #if i==j==4:
        #  print("HASHMATRIX A :")
        #  print(hashmatrixA)
        #  print(len(hashmatrixA))
          #hashmatrixA.clear()
          
        #  print(len(hashmatrixB))
        print("antes de mimir")
        time.sleep(8)
        print("despues de mimir")

        print("Sigue el paso 2")
        paso2()
        #else:
        #  continue
          
          #comparar aqui? si son iguales ejecutar funcion XX , si no .. pass (?)

        

  def paso2():
    print("Este es el paso 2")
    for i in range (1,5):
      for j in range (1,5):
        #a=f'D:\\Desktop\\NewTracker-Funciona_Sin_Threads\\Be4\\frames_0{i}_0{j}.png'
        #b=f'D:\\Desktop\\NewTracker-Funciona_Sin_Threads\\After\\frames_0{i}_0{j}.png'
        a=f'C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\Be4\\frames_0{i}_0{j}.png'
        b=f'C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After\\frames_0{i}_0{j}.png'
        shutil.copy(a,b)
    #os.chdir(r'D:\\Desktop\\NewTracker-Funciona_Sin_Threads\\After')
    #for i in range (1,5):
    #  for j in range (1,5):    
        #hashB=imagehash.average_hash(Image.open(f'frames_0{i}_0{j}.png'))
        #hashmatrixB.append(str(hashB))
        
        
    if i==j==4:

      print("HASHMATRIX B :")
      print(hashmatrixB)
      print("Previo al paso 3")
      time.sleep(2)
      paso3()
      
    
    #ac es donde deben compararse.
    
  def paso3():
    print("Inicio del paso 3")
    for i in range (0,16):
      #INTRODUCIR LOS HASHES EN CADA ARRAY, EN CARPETAS DIFERENTES.
      #HASHMATRIX DE LAS IMAGENES EN LA PRIMERA CARPETA
      #TRAERLAS DEL PATH BE4
      


      a=f'C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\Be4\\frames_0{i}_0{j}.png'



      #HASHMATRIX DE LAS IMAGENES EN LA SEGUNDA CARPETA
      #TRAERLAS DEL PATH AFTER
      



      #COMPARAR AMBAS MATRIX. 


      if hashmatrixA[i] == hashmatrixB[i]:
        print("esta es igual")
      else:
       print("esta nokz")

      if i==15:
    
        hashmatrixB.clear()
        hashmatrixA.clear()
        paso1()
      #  
      #  os.chdir(path)
      #  print("and finally 6th")



if __name__=='__main__':

    print("Si, si ..")
    #time.sleep(2)
    print("Si, si ..again")
    main()
    print("Y esto?")#guarda las imagenes en A y les asigna un hash. el hash se convierte a tipo string y se guarda en el array hashmatrix.
