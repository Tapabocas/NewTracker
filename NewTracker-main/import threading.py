import threading
import time  

def main():
    while True:
        def esperar8():
            print("Esto deberia esperar 8 segundos")
            time.sleep(8)
            print("Ya pasaron 8s")
            
    thread=threading.Thread(target=esperar8)
    thread.start()   

                

if __name__=='__main__':
    main()
