import os

try:
    from psutil import Process
except ImportError:
    print("Trying to Install required module: psutil\n")
    os.system('pip3 install psutil')