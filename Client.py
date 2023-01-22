import zmq
import threading
import time
from PyQt6.QtWidgets import *
import sys
from datetime import datetime
from multiprocessing import Queue
from PyQt6 import QtCore
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import random

class welcomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CrypText")
        self.setFixedSize(500,180)
        self.widgets()
        self.inputtedName = ""

    def widgets(self):
        self.taskName = QLabel("Please enter your name: ", self)
        self.taskName.setGeometry(180,20,200,60)
        self.nameInput = QLineEdit(self)
        self.nameInput.setGeometry(50,100,400,40)
        self.nameInput.returnPressed.connect(self.enteredInput)

    def enteredInput(self):
        self.inputtedName = self.nameInput.text()
        self.nameInput.hide()
        self.taskName.setText("Please wait to another user, and for establishing secure connection!")
        self.taskName.setGeometry(70,70,360,40)
    def getInputtedName(self):
        return self.inputtedName  

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CrypText")
        self.setFixedSize(1280,720)
        self.widgets()
        
        # setupUi
    def widgets(self):
        pushButton = QPushButton("Send message",self)
        pushButton.clicked.connect(self.addMessageToList)
        pushButton.setGeometry(1090, 560, 171, 91)
        
        self.lineEdit = QTextEdit(self)
        self.lineEdit.setGeometry(70, 560, 991, 101)
        self.lineEdit.setPlaceholderText("Type your message...")

        self.label = QLabel(self)
        self.label.setGeometry(350, 0, 611, 41)

        self.plainTextEdit = QPlainTextEdit(self)
        self.plainTextEdit.setGeometry(70, 50, 1181, 501)
        self.plainTextEdit.setReadOnly(True)

    def setLabel(self, text):
        self.label.setText(f"Chatting with {text}")

    def addMessageToList(self):
        global main_buffor
        now = datetime.now()
        messageDate = str(now.strftime("%d/%m/%Y %H:%M:%S"))
        temp_msg = self.lineEdit.toPlainText() 
        main_buffor.put(messageDate + " " + ownUserName + "\n" + temp_msg)
        self.lineEdit.clear()
        sendMessage(temp_msg)

    def addRecivedMessage(self,message):
        global main_buffor
        now = datetime.now()
        messageDate = str(now.strftime("%d/%m/%Y %H:%M:%S"))
        main_buffor.put(messageDate + " " + secondUser + "\n" + message)#
    
    def updateMainWindow(self, message):
        self.plainTextEdit.appendPlainText(message)


def updateMessage():
    while True:
        QtCore.QCoreApplication.processEvents()
        if not main_buffor.empty():
            window.updateMainWindow(main_buffor.get())
        #60 fps
        time.sleep((1/60))

def sendMessage(msg):
        global socket
        encryptedText = encryptMessage(bytes(msg, "utf-8"))
        socket.send(encryptedText)

def reciveMessage():
    global socket, window, Flag
    while True:
        QtCore.QCoreApplication.processEvents()
        message = socket.recv()
        #add decryption to message:
        decryptedText = decryptMessage(message)
        window.addRecivedMessage(decryptedText.decode("utf-8"))

def getSecureConnection(name, pubKey):
    print("Waitng for another user")
    context = zmq.Context()
    socket = context.socket(zmq.DEALER)
    port = 50001
    socket.setsockopt_string(zmq.IDENTITY, f"{name}")#_CONNECTION
    socket.connect("tcp://127.0.0.1:%s" %port)
    socket.send_string("Hello!")
    socket.send(pubKey)
    secondUserName = ""
    #wait for server to recive second user name
    while True:
        QtCore.QCoreApplication.processEvents()
        try:
            secondUserName = socket.recv(flags=zmq.NOBLOCK)
        except zmq.Again as e:
            continue
        if secondUserName != "":break
    userPublicKey = ""
    #wait for server, to get second user public key, to encrypy messages
    while True:
        QtCore.QCoreApplication.processEvents()
        try:
            userPublicKey = socket.recv(flags=zmq.NOBLOCK)
        except zmq.Again as e:
            continue
        if userPublicKey != b'-':break
    socket.close()
    return secondUserName.decode('utf-8'), RSA.import_key(userPublicKey)


def genKeys():
    #make folder in app and put here 100 private keys in .pem format
    #app will randomly take one of those keys and load as private key
    random_key = random.randint(0,99)
    key = open(f"private_keys/{random_key}.pem", "rb")
    #comment two lines upper and uncomment line below to use only one private key
    #key = open(f"private_keys.pem", "rb")
    private_key = RSA.import_key(key.read())
    public_key = private_key.publickey()
    return private_key, public_key

def encryptMessage(message):
    global userPublicKey
    cipher = PKCS1_OAEP.new(userPublicKey)
    encryptedText = cipher.encrypt(message)
    return encryptedText

def decryptMessage(endcryptedMessage):
    global privateKey
    cipher = PKCS1_OAEP.new(privateKey)
    try:
        decryptedHash = cipher.decrypt(endcryptedMessage)
    except:
        decryptedHash = bytes("Can't decrypt hash due to wrong key", encoding='utf-8')
    return decryptedHash

privateKey, publicKey = genKeys()
context = zmq.Context()
socket = context.socket(zmq.DEALER)
port = 50000
app = QApplication([])
window = Window()
welcomeScreen = welcomeWindow()
welcomeScreen.show()
uniqe_id =  ""
while uniqe_id == "":
    QtCore.QCoreApplication.processEvents()
    uniqe_id = welcomeScreen.getInputtedName()
uniqe_id = bytes(uniqe_id.encode('utf-8'))
ownUserName = uniqe_id.decode('utf-8')
secondUser, userPublicKey = getSecureConnection(ownUserName, publicKey.export_key())
window.setLabel(secondUser)


main_buffor = Queue()

def main():
    socket.setsockopt(zmq.IDENTITY, uniqe_id)
    #socket.connect("tcp://localhost:%s" %port)
    socket.connect("tcp://127.0.0.1:%s" %port)
    rcvMSG = threading.Thread(target=reciveMessage)
    upMSG = threading.Thread(target=updateMessage)
    upMSG.start()
    rcvMSG.start()
    welcomeScreen.hide()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
