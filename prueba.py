import time
from lauda import Lauda
parar = False

lauda = Lauda()
lauda.open(url="169.254.87.54:54321")
lauda.start()
lauda.set_t_set(0)

temp = 0
while not parar:
    time.sleep(5)
    if(float(lauda.get_t_ext()) >= 0.0 and float(lauda.get_t_ext()) <= 0.2):
        time.sleep(60)
        while not parar:
            lauda.set_t_set(temp - 1)
            if(float(lauda.get_t_set()) != -10):
                temp = temp - 1

            time.sleep(60)

            if (float(lauda.get_t_ext()) <= -10):
                print("HEMOS LLEGADO")
                parar = True

lauda.stop()