import imagehash
from PIL import Image
import time
import image_slicer
arrayprueba=[]
while True:
    arrayprueba.clear()
    hash=imagehash.average_hash(Image.open(f'frames_01_01.png'))
    imagenesPartidas=image_slicer.slice("frames.jpg",16)

    print(hash)
    print(type(imagenesPartidas))
    print(len(imagenesPartidas))
    arrayprueba.append(hash)    
    print(arrayprueba)
    time.sleep(1)