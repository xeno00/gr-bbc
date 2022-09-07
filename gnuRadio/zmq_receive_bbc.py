#import sys
#import time
import zmq
import random
import numpy as np
import sys
import threading
from multiprocessing import Queue
import time

#import subprocess
#import matplotlib.pyplot as plt


# numpy options
np.set_printoptions(threshold=sys.maxsize)

thePort = '5555'
exit_flag = False
ip = "tcp://127.0.0.1"


def consumer(exit_flag):
    consumer_id = random.randrange(1,10005)
    print("I am consumer #%s" % (consumer_id))
    context = zmq.Context()
    consumer_receiver = context.socket(zmq.PULL)
    consumer_receiver.connect(ip + ":" + thePort)
    while True:
        #time.sleep(1)
        #subprocess.run([sys.executable, grcFile, "--port", thePort])
        dataq.put(consumer_receiver.recv())
        # exit flag?
        if exit_flag():
            consumer_receiver.close()
            time.sleep(0.5)
            context.term()
            time.sleep(0.5)
            break

def main():
    exit_flag = False
    #set up  multithreading
    rxThread = threading.Thread(target=consumer, args=(lambda : exit_flag, ))
    rxThread.daemon = True
    rxThread.start() # start the receive thread
    i = 0
    wait_counter = 0 
    while True:
        try:
            if (dataq.empty()) and (i>0): # assume we've received all the data
                if wait_counter < 20: # 20 is an arbitrary number, 20*0.1s = 2s seems like a reasonable length of time to wait
                    wait_counter +=1
                    time.sleep(0.1)
                else: # might need to do some data cleanup here 
                    print("Data queue is empty and I'm exiting")
                    exit_flag = True
                    time.sleep(1)
                    break
            else:
                wait_counter = 0 # reset the wait counter in case we've been waiting
                buff=dataq.get()
                #print(buff.decode('utf-8') + "\n") # for bytes
                #data = np.frombuffer(buff, dtype="float32")
                #print(data)
                try:
                    #print(''.join([chr(int(itm)) for itm in data])) # ascii
                    print(buff)
                    #print(buff.decode('utf-8') + "\n")  # for bytes
                except: 
                    print("Error on decoding, moving on.")
                #print("Received data, length = " + str(len(data)))
                #buff = []
                #print()
            i+=1
        except KeyboardInterrupt:
            #consumer_receiver.close()
            #context.term()
            exit_flag = True
            print("Exiting")
            #rxThread.join()
            #print("Closing threads, please wait...")
            time.sleep(0.5)
            #sys.exit()
    #sys.exit()


if __name__ == "__main__":
    dataq = Queue()
    main()


