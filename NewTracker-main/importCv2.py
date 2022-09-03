#guarda las imagenes en A y les asigna un hash. el hash se convierte a tipo string y se guarda en el array hashmatrix.
# what if saco el hash DESPUÉS de que las imagenes sean distintas..  . . . ...............
from glob import has_magic
import cv2
import numpy as np
import image_slicer
import imagehash
import timeit
from PIL import Image
import os
import time
from difflib import SequenceMatcher
import shutil

not_equal=[]
hashmatrixA=[]
hashmatrixB=[]
def main():

  path = r'C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\Be4'
  pathB = r'C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After'



  def paso1():
    #Borrar los cuadros tambien
    
    not_equal.clear()
    hashmatrixA.clear()
    hashmatrixB.clear()
    print("SE ESTA CAPTURANDO")
    os.chdir(path)
    #captura = cv2.VideoCapture('rtsp://192.168.1.64/1)
    captura = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if (captura.isOpened()):
      ret, imagen = captura.read()  
      if ret:
        cv2.imwrite("frames.jpg" , imagen)
        image_slicer.slice("frames.jpg",16)



    print("CREACION DE HASHES DE A, CREANDO ...")
  
    PWD=str(os.getcwd())
    print(PWD)
    for i in range (1,5):
      for j in range (1,5):
        hashA=imagehash.phash(Image.open(f'frames_0{i}_0{j}.png'))
        hashmatrixA.append(str(hashA))

        if j==i==4:

          print("HASHMATRIX A :")
          print(hashmatrixA)
          print("HASHES DE A CREADOS REI, SIGUE LA CREACION DE LOS OTROS ...")

          
    os.chdir(pathB)
    for i in range (1,5):
      for j in range(1,5):
        hashB=imagehash.phash(Image.open(f'frames_0{i}_0{j}.png'))
        hashmatrixB.append(str(hashB))
        if j==i==4:
          print("HASHMATRIX B :")
          print(hashmatrixB)
          print("HASHES DE B CREADOS REI SIGUE EL PASO 4: NO SE KUAL EZ XD ")
          time.sleep(3)
        
          paso2() 

  def paso2():

    print("COPIANDO DE A a B ...")
    tic=timeit.default_timer()
    for i in range (1,5):
      for j in range (1,5):
        #a=f'D:\\Desktop\\NewTracker-Funciona_Sin_Threads\\Be4\\frames_0{i}_0{j}.png'
        #b=f'D:\\Desktop\\NewTracker-Funciona_Sin_Threads\\After\\frames_0{i}_0{j}.png'
        a=f'C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\Be4\\frames_0{i}_0{j}.png'
        b=f'C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After'
        shutil.copy(a,b)
          
        if i==j==4:
          toc=timeit.default_timer()
          print(f"COPIADO REALIZADO CON t= {toc-tic}..")
          paso4()

  def paso4():
   #IDENTIFICAR LOS HAASHES DISTINTOS
    for i in range (0,16):
        comp=similar(hashmatrixA[i],hashmatrixB[i])
        if comp>0.35:
          print(f"Estos son IGUALES  {i}  "+"DE A :"+hashmatrixA[i]+"DE B:" + hashmatrixB[i])
        else: 
          print(f"Estos son DISTINTOS  {i}  "+"DE A :"+hashmatrixA[i]+"DE B:" + hashmatrixB[i])
          not_equal.append(i)

          print("INDICES DISTINTOS:")
          print(not_equal)

         # cv2.line('frames_'0)
    convert_1d_to_2d_array()
    #paso1()

  def similar(a,b):  
      return SequenceMatcher(None,a,b).ratio()
      

  def convert_1d_to_2d_array():
   #could put these inside a function .. inside a loop
    for different in not_equal:
      if different==0:
        image=cv2.imread('C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After\\frames_01_01.png')
        
        #image2=cv2.imwrite()
        imagen=cv2.rectangle(image,pt1=(0,120),pt2=(160,120),color=(0,0,255), thickness=20)
        cv2.imwrite("frames_01_01.png", imagen)

      elif different==1:
        image=cv2.imread('C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After\\frames_01_02.png')
        
        #image2=cv2.imwrite()
        imagen=cv2.rectangle(image,pt1=(0,120),pt2=(160,120),color=(0,0,255), thickness=20)
        cv2.imwrite("frames_01_02.png", imagen)
      elif different==2:
        image=cv2.imread('C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After\\frames_01_03.png')
        
        #image2=cv2.imwrite()
        imagen=cv2.rectangle(image,pt1=(0,120),pt2=(160,120),color=(0,0,255), thickness=20)
        cv2.imwrite("frames_01_03.png", imagen)
      elif different==3:
        image=cv2.imread('C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After\\frames_01_04.png')
        
        #image2=cv2.imwrite()
        imagen=cv2.rectangle(image,pt1=(0,120),pt2=(160,120),color=(0,0,255), thickness=20)
        cv2.imwrite("frames_01_04.png", imagen)
      elif different==4:
        image=cv2.imread('C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After\\frames_02_01.png')
        
        #image2=cv2.imwrite()
        imagen=cv2.rectangle(image,pt1=(0,120),pt2=(160,120),color=(0,0,255), thickness=20)
        cv2.imwrite("frames_02_01.png", imagen)
      elif different==5:
        image=cv2.imread('C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After\\frames_02_02.png')
        
        #image2=cv2.imwrite()
        imagen=cv2.rectangle(image,pt1=(0,120),pt2=(160,120),color=(0,0,255), thickness=20)
        cv2.imwrite("frames_02_02.png", imagen)
      elif different==6:
        image=cv2.imread('C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After\\frames_02_03.png')
        
        #image2=cv2.imwrite()
        imagen=cv2.rectangle(image,pt1=(0,120),pt2=(160,120),color=(0,0,255), thickness=20)
        cv2.imwrite("frames_02_03.png", imagen)
      elif different==7:
        image=cv2.imread('C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After\\frames_02_04.png')
        
        #image2=cv2.imwrite()
        imagen=cv2.rectangle(image,pt1=(0,120),pt2=(160,120),color=(0,0,255), thickness=20)
        cv2.imwrite("frames_02_04.png", imagen)
      elif different==8:
        image=cv2.imread('C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After\\frames_03_01.png')
        
        #image2=cv2.imwrite()
        imagen=cv2.rectangle(image,pt1=(0,120),pt2=(160,120),color=(0,0,255), thickness=20)
        cv2.imwrite("frames_03_01.png", imagen)
      elif different==9:
        image=cv2.imread('C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After\\frames_03_02.png')
        
        #image2=cv2.imwrite()
        imagen=cv2.rectangle(image,pt1=(0,120),pt2=(160,120),color=(0,0,255), thickness=20)
        cv2.imwrite("frames_03_02.png", imagen)
      elif different==10:
        image=cv2.imread('C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After\\frames_03_03.png')
        
        #image2=cv2.imwrite()
        imagen=cv2.rectangle(image,pt1=(0,120),pt2=(160,120),color=(0,0,255), thickness=20)
        cv2.imwrite("frames_03_03.png", imagen)
      elif different==11:
        image=cv2.imread('C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After\\frames_03_04.png')
        
        #image2=cv2.imwrite()
        imagen=cv2.rectangle(image,pt1=(0,120),pt2=(160,120),color=(0,0,255), thickness=20)
        cv2.imwrite("frames_03_04.png", imagen)
      elif different==12:
        image=cv2.imread('C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After\\frames_04_01.png')
        
        #image2=cv2.imwrite()
        imagen=cv2.rectangle(image,pt1=(0,120),pt2=(160,120),color=(0,0,255), thickness=20)
        cv2.imwrite("frames_04_01.png", imagen)
      elif different==13:
        image=cv2.imread('C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After\\frames_04_02.png')
        
        #image2=cv2.imwrite()
        imagen=cv2.rectangle(image,pt1=(0,120),pt2=(160,120),color=(0,0,255), thickness=20)
        cv2.imwrite("frames_04_02.png", imagen)
      elif different==14:
        image=cv2.imread('C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After\\frames_04_03.png')
        
        #image2=cv2.imwrite()
        imagen=cv2.rectangle(image,pt1=(0,120),pt2=(160,120),color=(0,0,255), thickness=20)
        cv2.imwrite("frames_04_03.png", imagen)
      elif different==15:
        image=cv2.imread('C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After\\frames_04_04.png')
        
        #image2=cv2.imwrite()
        imagen=cv2.rectangle(image,pt1=(0,120),pt2=(160,120),color=(0,0,255), thickness=20)
        cv2.imwrite("frames_04_04.png", imagen)
    paso1()






  paso1()

if __name__=='__main__':

    print("Si, si ..")
    #time.sleep(2)
    print("Si, si ..again")
    main()
    print("Y esto?")#guarda las imagenes en A y les asigna un hash. el hash se convierte a tipo string y se guarda en el array hashmatrix.
