#guarda las imgs en B
import shutil
for i in range (1,5):
    for j in range (1,5):
        a=f'frames_0{i}_0{j}.png'
        b=f'C:\\Users\\Camilo Palacios\\Desktop\\NewTracker-main\\After\\frames_0{i}_0{j}.png'
        shutil.copy(a,b)