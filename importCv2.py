def main():
  import cv2
  import numpy as np
  import image_slicer
  import imagehash
  from PIL import Image
  import base64
  


  while True: 
    captura = cv2.VideoCapture('http://192.168.14.22:8083/video_feed')
    framerate=captura.get(2) # Se guarda la imagen cada 2 segundos..
    while (captura.isOpened()):
      ret, imagen = captura.read()
      if ret:
        #cv2.imshow('video', imagen)   #no necesito ver la imagen completa, but la imagen compuesta de las pieces.
        cv2.imwrite("frames.jpg" , imagen)
        imagenesPartidas=image_slicer.slice("frames.jpg",16)
        print(type(imagenesPartidas))
        print(len(imagenesPartidas))
      else:
        continue
    
    b64matrix=[]


    import os
    path_of_the_directory =r"C:\Users\Camilo Palacios\Desktop\David\Python}"
    ext = ('.png')
    for files in os.listdir(path_of_the_directory):
        if files.endswith(ext): 
          with open(files, "rb") as img_file:
            my_string = base64.b64encode(img_file.read())
            
           # my_string = my_string.decode('utf-8')
            b64matrix.append(files)
        else:
            continue
    print(b64matrix)

  #pedir imagenes x,y para poder enviar las imagenes en base 64.
  #def cvt_2_base64(file_name):
  #  with open(file_name , "rb") as image_file :
  #      data = base64.b64encode(image_file.read())
  #      asno= data.decode('utf-8')
  #  print(asno)





  #  for i in range (1,16):
  #      with open("frames_0"+i+"_0"+i+".png", "rb") as img_file :
  #          string = base64.encodestring(img_file.read())
  #          b64matrix.append(string)
  #          #print(string)

#with open("grayimage.png", "rb") as img_file:
#b64_string = base64.b64encode(img_file.read())
#print(b64_string)

#Hacer primero la matriz de imagenes que se imprima bien, luego crear matriz de hashes.    
#Para crear la matriz de imagenes, tienen que estar en base 64 .. so convertirlas antes:


    #while True:
   #   matrix =[]
   #   for i in range (1,17):
   #     for j in range(1,17):
        #  matrix.append(cv2.imread("frames_0_"+i+"_0"+j+".png")) #Matriz de imagenes

      #hashmatrix=[]
      #for imagen in matrix:
      #  hash = imagehash.average_hash(Image.open(imagen))
      #  hashmatrix.append(hash)

      #print(hashmatrix)




if __name__=='__main__':
    main()

