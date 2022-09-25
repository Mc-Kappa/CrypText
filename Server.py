#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#
from logging import raiseExceptions
import sys
import zmq
import threading
import time
import queue

buforOfMessages = queue.Queue()
lock = threading.Lock()
context = zmq.Context()
socket = context.socket(zmq.ROUTER)
socket.bind("tcp://*:5555")

context2 = zmq.Context()
socket2 = context.socket(zmq.ROUTER)
socket2.bind("tcp://*:5556")


def reciveMessage():
    while True:
        global socket, lock, buforOfMessages
        person = socket.recv()
        message = socket.recv()
        print("Recived message from 1")
        lock.acquire()
        buforOfMessages.put(person)
        buforOfMessages.put(message)
        lock.release()

def reciveMessage2():
    while True:
        global socket, lock, buforOfMessages
        person = socket2.recv()
        message = socket2.recv()
        print("Recived message from 2")
        lock.acquire()
        buforOfMessages.put(person)
        buforOfMessages.put(message)
        lock.release()

def sendMessage():
    time.sleep(2)
    print("Started sending message!")
    while True:
        global socket,socket2, lock, buforOfMessages
        if (buforOfMessages.empty() == False):
            lock.acquire()
            userToSend = buforOfMessages.get() 
            messageToSend = buforOfMessages.get()
            print(messageToSend, userToSend)
            lock.release()
        #due to python 3.9 version i cant use match statment so i will go with if elif 
            print("Send message to %s" %userToSend)
            user1 = 'delta'.encode('utf-8')
            user2 = 'kappa'.encode('utf-8')
            if (userToSend == bytes(user1)):
                print("send to %s", userToSend)
                socket.send(messageToSend)
            elif (userToSend == bytes(user2)):
                socket2.send(messageToSend)
        #time.sleep(1)

rcvMSG = threading.Thread(target=reciveMessage)
rcvMSG2 = threading.Thread(target=reciveMessage2)
sndMSG = threading.Thread(target=sendMessage)

print("Hello on server of CrypText pre-alpha 0.0.1 v, server will run forever, until die")
rcvMSG.start()
rcvMSG2.start()
sndMSG.start()

print("type KILL to end server:")
print("\n")
temp = input()
if (temp == "KILL"):
    sys.exit(0)