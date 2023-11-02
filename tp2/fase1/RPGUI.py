import socket
import threading
import tkinter as tk

class RPGUI:

    def __init__(self, ip, portaClient, portaServer):
        self.IP = ip
        self.PORTACLIENT = portaClient
        self.PORTASERVER = portaServer
        self.socketForServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.socketForServer.bind((ip, portaServer))
        self.socketForClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.socketForClient.bind((ip, portaClient))

    def parse(self, file):
        with open(file, 'r') as f:
            for line in f:
                print(line)
    
    def startRP(self):
        thread0 = threading.Thread(target=self.clientConnection)
        thread0.start()

    def clientConnection(self):
        socket_address = (self.IP, self.PORTACLIENT)
        self.socketForClient.bind(socket_address)
        self.socketForClient.listen()
        print("RP à espera de conexão de Clientes: ", socket_address)
        while True:
            conn, addr = self.socketForClient.accept()
            print(f"Cliente {addr} conectado!")
            thread = threading.Thread(target=self.processClient, args=(conn, addr))
            thread.start()
            #self.processClient(conn, addr)

    def processClient(self, conn, addr):
        print(f"Processing {addr}")
        conn.close()

if __name__ == "__main__":
    try:
        ip = '127.0.0.1'
        portaClient = 12345
        portaServer = 12346

        # Criar um RP
        rp = RPGUI(ip, portaClient, portaServer)
        # rp.parse(file)
        rp.startRP()
    except:
        print("[Usage: RP.py]\n")	