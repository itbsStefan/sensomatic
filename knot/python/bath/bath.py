import Queue
import serial
import time
import paho.mqtt.client as mqtt
import threading

sendQueue    = Queue.Queue()

class ReceiveThread(threading.Thread):

    def __init__(self, ser, mqclient):
        threading.Thread.__init__(self)
        self._ser      = ser
        self._mqclient = mqclient

    def run(self):
        while True:
            line    = self._ser.readline()
            element = line.split(',')
            command = int(element[0])
            if (command == 0):
                #print "Ack Comment"
                pass
            if (command == 1):
                print "Error:%s" % line
            if (command == 2):
                print "Set R"
            if (command == 3):
                print "Set R"
            if (command == 4):
                print "Set B"
            if (command == 5):
                print "GetTemp"
            if (command == 6):
                print "GetHumidity"
            if (command == 7):
                print "GetLight"
            if (command == 10):
                temp = float(element[1].split(";")[0])
                #print "Temp:%f" % temp
                self._mqclient.publish("bathroom/temperature", temp)
            if (command == 11):
                hum = float(element[1].split(";")[0])
                #print "Humidity:%f"  % hum
                self._mqclient.publish("bathroom/humidity", hum)
            if (command == 12):
                light = float(element[1].split(";")[0])
                #print "Light:%d"  % light
                self._mqclient.publish("bathroom/light", light)
            if (command == 13):
                button = int(element[1].split(";")[0])
                print "Button Pressed:%d" % button
                self._mqclient.publish("bathroom/button", button)

class SendThread(threading.Thread):
    """Threaded serial send"""

    def __init__(self, queue, ser):
        threading.Thread.__init__(self)
        self._queue = queue
        self._ser   = ser

    def run(self):
        while True:
            line = self._queue.get()
            self._ser.write(line + "\n")
            self._queue.task_done()
            time.sleep(0.5) # Give him time to react

class TasksThread(threading.Thread):
    """Threaded measurement"""

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self._queue = queue

    def run(self):
        while True:
            time.sleep(5)
            self._queue.put("5;") # Temperature
            self._queue.put("6;") # Humidity
            self._queue.put("7;") # Light

def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("bathroom/light/+")

def on_message(client, userdata, msg):
    print "Mq Received on channel %s -> %s" % (msg.topic, msg.payload)
    parts   = msg.topic.split("/")
    channel = parts[2]
    vals    = msg.payload.split(",")
    sendQueue.put("2,%d;" % int(vals[0]))
    sendQueue.put("3,%d;" % int(vals[1]))
    sendQueue.put("4,%d;" % int(vals[2]))

if __name__ == "__main__":
    print "Start"

    ser = serial.Serial("/dev/ttyAMA0", 9600)

    mqclient = mqtt.Client("bathroom", clean_session=True)
    mqclient.connect("cortex", 1883, 60)
    mqclient.on_connect = on_connect
    mqclient.on_message = on_message

    receive = ReceiveThread(ser, mqclient)
    receive.setDaemon(True)
    receive.start()

    send = SendThread(sendQueue, ser)
    send.setDaemon(True)
    send.start()

    tasks = TasksThread(sendQueue)
    tasks.setDaemon(True)
    tasks.start()

    mqclient.loop_forever()