import socket
import threading
import tkinter as tk

class RPGUI:

    def __init__(self, ip, portaClient, portaServer):
        self.IP = ip
        self.PORTACLIENT = portaClient
        self.PORTASERVER = portaServer
        self.socketForServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketForClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.streamList = []
        #self.parse()
        self.startRP()

    def parse(self, file):
        with open(file, 'r') as f:
            for line in f:
                print(line)
    
    def startRP(self):
        thread0 = threading.Thread(target=self.clientConnection)
        thread1 = threading.Thread(target=self.serverConnection)
        thread0.start()
        thread1.start()

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

    def processClient(self, conn, addr):
        print(f"Processing {addr}")
        conn.close()
    
    def serverConnection(self):
        socket_address = (self.IP, self.PORTASERVER)
        self.socketForServer.bind(socket_address)
        self.socketForServer.listen()
        print("RP à espera de conexões de Servidores: ", socket_address)
        while True:
            conn, addr = self.socketForServer.accept()
            print(f"Servidor {addr} conectado!")
            thread = threading.Thread(target=self.processServer, args=(conn, addr))
            thread.start()

    def processServer(self, conn, addr):
        print(f"Processing {addr}")
        # perguntar quais os videos que o servidor tem para transmitir
        # receber mensagens com o nome dos videos
        message = conn.recv(1024)
        # Processar e responder às mensagens recebidas aqui
        print(f"Mensagem recebida: {message.decode('utf-8')}")
        conn.close()


if __name__ == "__main__":
    try:
        ip = '127.0.0.1'
        portaClient = 12345
        portaServer = 12346

        # Criar um RP
        rp = RPGUI(ip, portaClient, portaServer)
    except:
        print("[Usage: RP.py]\n")	