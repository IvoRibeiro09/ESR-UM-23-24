import socket
import threading
from time import sleep
import tkinter as tk
from auxiliarFunc import *
import queue

class RPGUI:

    def __init__(self, file):
        #self.IP = getIP
        self.IP = '127.0.0.1'
        self.PORTACLIENT = None
        self.PORTASERVER = None
        self.socketForServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketForClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.streamList = []
        self.condition = threading.Condition()
        self.clientQueue = queue.Queue(maxsize=10)
        self.streamsPlayingList = []
        self.parse(file)
        self.startRP()

    def parse(self, file):
        print("Parsing...")
        with open(file, 'r') as f:
            read = False
            for line in f:
                if f"ip- {self.IP}" in line:
                    read = True
                if read:
                    if "------" in line:
                        break
                    elif "portaClient- " in line:
                        self.PORTACLIENT = extrair_numero_porta(line)
                    elif "portaServer- " in line:
                        self.PORTASERVER = extrair_numero_porta(line)

    def startRP(self):
        print("Starting...")
        thread0 = threading.Thread(target=self.clientConnection)
        thread1 = threading.Thread(target=self.serverConnection)
        thread0.start()
        thread1.start()

    # Tratamento de Clientes
    def clientConnection(self):
        socket_address = (self.IP, self.PORTACLIENT)
        self.socketForClient.bind(socket_address)
        self.socketForClient.listen()
        print("RP à espera de conexão de Clientes: ", socket_address)
        try:
            while True:
                conn, addr = self.socketForClient.accept()
                print(f"Cliente {addr} conectado!")
                thread = threading.Thread(target=self.processClient, args=(conn, addr))
                thread.start()
        finally:
            self.socketForClient.close()

    def processClient(self, conn, addr):
        print(f"Processing Client: {addr}")
        try:
            self.initialClientConn(conn, addr)
            self.streamTransmition(conn, addr)

        finally:
            # Feche o socket do cliente
            conn.close()
        
    def initialClientConn(self, conn, addr):
        try:
            # Receber msg de quais videos tem
            data = conn.recv(1024)
            mensagem = data.decode()

            if mensagem == "VideoList":
                # Envie a lista de vídeos de volta ao cliente
                if not self.streamList:
                    noVidmsg = "I DONT HAVE STREAMS"
                    conn.sendall(noVidmsg.encode())
                else:
                    msg = ""
                    for video in self.streamList:
                        msg = msg+f"{video}/"    
                    conn.sendall(msg.encode())
                print("Lista de vídeos enviada ao cliente: ",addr)
            else:
                print("Mensagem não reconhecida:", mensagem)
        except Exception as e:
            print("Erro durante a comunicação com o cliente:", str(e))

    def streamTransmition(self, conn, addr):
        #esperar receber uma mensagem do cliente com qual video da lista quer assistir
        data = conn.recv(1024)
        mensagem = data.decode()
        vid = extrair_conteudo(mensagem)
        print(f"Cliente {addr} pediu a visualização da stream: {vid}")
        # adicionar à lista queue o video pedido
        # notifiacar os servidores
        with self.condition:
            self.clientQueue.put(vid)
            self.condition.notifyAll()

    # Tratamento de Servidores
    def serverConnection(self):
        socket_address = (self.IP, self.PORTASERVER)
        self.socketForServer.bind(socket_address)
        self.socketForServer.listen()
        print("RP à espera de conexões de Servidores: ", socket_address)
        try:
            while True:
                conn, addr = self.socketForServer.accept()
                print(f"Servidor {addr} conectado!")
                thread = threading.Thread(target=self.processServer, args=(conn, addr))
                thread.start()
        finally:
            self.socketForServer.close()

    def processServer(self, conn, addr):
        print(f"Processing Server: {addr}")
        try:
            self.initialServerConnection(conn, addr)
            self.recibeServerStream(conn, addr)
        finally:
            conn.close()
    
    def initialServerConnection(self, conn, addr):
        # perguntar quais os videos que o servidor tem para transmitir
        # receber mensagens com o nome dos videos
        data = conn.recv(1024)
        mensagem = data.decode('utf-8')
        # Processar e responder às mensagens recebidas aqui
        self.updateVideoList(mensagem)
        #aguardar que o seja solicitado um video para pedir ao server
        with self.condition:
            check = False
            while not check:
                self.condition.wait()
                check = self.checkIfServer(mensagem)
        # é o servidor com o video que o cliente pediu
        stream = self.clientQueue.get()
        # enviar pedido ao servidor para enviar o video
        msgToSend = f'Stream- {stream}'
        conn.sendall(msgToSend.encode())
        print(f"Enviou requisição para Stream: {stream} - {addr}")


    def updateVideoList(self, mensagem):
        vids = mensagem.split('-ADD-')
        vids.pop()
        for video in vids:
            self.streamList.append(video)

    def checkIfServer(self, mensagem):
        try:
            selectedStream = self.clientQueue.get(timeout=1)  # Aqui você obtém o elemento da fila, com um tempo limite de 1 segundo
            self.clientQueue.put(selectedStream)  # Devolve o elemento à fila (se desejar)
            return selectedStream in mensagem
        except queue.Empty:
            return False

    def recibeServerStream(self, conn, addr):
        print("A receber stream de: ", addr)
        sleep(15)
        

if __name__ == "__main__":
    try:
        filename = "config_file.txt"
        # Criar um RP
        rp = RPGUI(filename)
    except:
        print("[Usage: RP.py]\n")	