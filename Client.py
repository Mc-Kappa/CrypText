#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#
import zmq
import threading
import time
def sendMessage():
    time.sleep(2)
    global socket, temp_arr
    while True:    
        print("What do you want to say?: ")
        textToSend = input()
        print(temp_arr)
        socket.send_string(textToSend)
        #(bytes(textToSend, 'utf-8'))

def reciveMessage():
    global socket, temp_arr
    print("im reciving!")
    while True:
        message = socket.recv()
        print("WTF")
        temp_arr.append(message)
        print("Received reply %s" %message)

context = zmq.Context()
socket = context.socket(zmq.DEALER)

print("Choose port to connect from 5555 to 5556:")
port = input()

print("Give me your id: ")
id = bytes(input().encode('utf-8'))

while True:
    if (int(port) == 5555 or int(port) == 5556):
        print("Good choice")
        break
    else:
        print("You stupid, take a good port damn, 5555 or 5556")
        port = input()

socket.setsockopt(zmq.IDENTITY, id)
socket.connect("tcp://localhost:%s" %port)
temp_arr = [] 
rcvMSG = threading.Thread(target=reciveMessage)
sndMSG = threading.Thread(target=sendMessage)

rcvMSG.start()
sndMSG.start()
