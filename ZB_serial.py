#-*- conding:utf-8 -*-
import serial
import time
import json
import threading
from time import ctime,sleep
import queue
import sqlite3
q = queue.Queue()
ser = serial.Serial("COM5",115200)
def Zigbee():
    while True:
        count = ser.inWaiting()
        if count != 0:
            recvs = ser.read(ser.in_waiting).decode('utf-8')#.split(':')[1]
            # 读出串口数据，数据采用utf-8解码
            recv = str(recvs).split('C')[0]
            #recv = ser.readline().split('C')[0]
            #recv1 = ser.read(ser.inWaiting())
            ser.flushInput()
            q.put(recv)
            data = str(recv)
            print(data)
        sleep(2)

def Zigbee_json ():
    global recv
    while True:
        if q.empty():
            pass
        else:
            data = q.get('utf-8')
            #con = sqlite3.connect('wendu.db')
            #c = con.cursor()
            #c.execute("INSERT INTO DEVICE (temp)values ('{}')".format(data))
            #con.commit()
            #con.close()
            tmp_output = open("tmp_data1.txt",'w')
            tmp_output.write(data)
            tmp_output.flush()
            tmp_output.close()
            print(data)
            sleep(2)
            
    
threads = []
t1 = threading.Thread(target = Zigbee)
threads.append(t1)
t2 = threading.Thread(target = Zigbee_json)
threads.append(t2)
if __name__ == '__main__':
    for t in threads:
        t.start()
    t1.join()
    t2.join()
    while True:
        sleep(2)
