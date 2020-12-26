#-*-coding:utf-8 -*-
from __future__ import print_function
import time
import paho.mqtt.client as mqtt
import struct
import json
import datetime
import sqlite3

# CONNECT 方式：
# client_id:     DEV_ID
# username:  PRO_ID
# password:   AUTHINFO(鉴权信息)
# 可以连接上设备云，CONNECT 和 CONNACK握手成功
# temperature:已创建的一个数据流
#更多请查阅OneNet官方mqtt文档与paho-mqtt开发文档

#修改成自己的即可
DEV_ID = "635692756" #设备ID
PRO_ID = "375535" #产品ID
AUTH_INFO = "11111111111111111111111111111111111"  #jianquan
temperature=''
def read():
    global temperature
    with open("tmp_data1.txt") as file:
        temperature = str(file.read())

    #humidity= float(20)
time1 = datetime.datetime.now().isoformat()

TYPE_JSON = 0x01
TYPE_FLOAT = 0x17


def build_payload(type, payload):
    datatype = type
    packet = bytearray()
    packet.extend(struct.pack("!B", datatype))
    if isinstance(payload, str):
        udata = payload.encode('utf-8')
        length = len(udata)
        packet.extend(struct.pack("!H" + str(length) + "s", length, udata))
    return packet

# 当客户端收到来自服务器的CONNACK响应时的回调。也就是申请连接，服务器返回结果是否成功等
def on_connect(client, userdata, flags, rc):
    read()
    time.sleep(3)
    print("连接结果:" + mqtt.connack_string(rc))
    #上传数据
    body = {
        "datastreams": [
            {
                "id": "temp",  # 对应OneNet的数据流名称
                "datapoints": [
                    {
                        "at": time1,  # 数据提交时间，这里可通过函数来获取实时时间
                        "value": temperature  # 数据值
                    }
                ]
            }
        ]
    }

    json_body = json.dumps(body)
    packet = build_payload(TYPE_JSON, json_body)
    client.publish("$dp", packet, qos=1)  # qos代表服务质量

    con = sqlite3.connect('wendu.db')
    c = con.cursor()
    c.execute("INSERT INTO DEVICE (temp)values ('{}')".format(temperature))
    con.commit()
    con.close()


# 从服务器接收发布消息时的回调。
def on_message(client, userdata, msg):
    print("温度:"+str(msg.payload,'utf-8')+"%RH")


#当消息已经被发送给中间人，on_publish()回调将会被触发
def on_publish(client, userdata, mid):
    print("mid:" + str(mid))
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_message = on_message
    client.username_pw_set(username=PRO_ID, password=AUTH_INFO)
    client.connect('183.230.40.39', port=6002, keepalive=120)

def main():
    client = mqtt.Client(client_id=DEV_ID, protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_message = on_message
    client.username_pw_set(username=PRO_ID, password=AUTH_INFO)
    client.connect('183.230.40.39', port=6002, keepalive=120)
    client.loop_forever()

if __name__ == '__main__':
    while True:
        
        main()

