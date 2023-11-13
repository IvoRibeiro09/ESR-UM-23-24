import socket
import threading
from time import sleep
import tkinter as tk
from auxiliarFunc import *
from connectionProtocol import Packet as pack
from Stream import *

class Cliente:
    def __init__(self, conn, addr):
        self.ip = addr[0]
        self.porta = addr[1]       
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket = conn

    def initialClientConn(self, streamList):
        try:
            # Receber msg de quais videos tem
            data = self.client_socket.recv(1024)
            mensagem = data.decode()

            if mensagem == "VideoList":
                # Envie a lista de vídeos de volta ao cliente
                if not streamList:
                    noVidmsg = "I DONT HAVE STREAMS"
                    self.client_socket.sendall(noVidmsg.encode())
                else:
                    msg = ""
                    for stream in streamList:
                        msg = msg+f"{Stream.getName(stream)}/"    
                    self.client_socket.sendall(msg.encode())
                print("Lista de vídeos enviada ao cliente: ",self.ip)
            else:
                print("Mensagem não reconhecida:", mensagem)
                return None
            data = self.client_socket.recv(1024)
            mensagem = data.decode()
            vid = extrair_conteudo(mensagem)
            print(f"Cliente {self.ip} pediu a visualização da stream: {vid}")
            return vid
        except Exception as e:
            print("Erro durante a comunicação com o cliente:", str(e))
            return None
        
class Server:
    def __init__(self, conn, addr):
        self.ip = addr[0]
        self.porta = addr[1]       
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket = conn

    def initialServerConnection(self, conn, addr):
        # perguntar quais os videos que o servidor tem para transmitir
        # receber mensagens com o nome dos videos
        data = self.client_socket.recv(1024)
        mensagem = data.decode('utf-8')
        evento = threading.Event()
        # Processar e responder às mensagens recebidas aqui
        self.updateVideoList(mensagem, evento)

        '''
        #aguardar que o seja solicitado um video para pedir ao server
        waiting = True
        while waiting:
            evento.wait()
            askedStream = self.checkWhatStream()
            if askedStream != None:
                # enviar mensagem pro server dizer qual vai ser o video escolhido
                msgToSend = "Stream- " + Stream.getName(askedStream)
                conn.sendall(msgToSend.encode('utf-8'))
                print(f"Enviou requisição de {Stream.getName(askedStream)} para Stream: {addr}")
                thread = threading.Thread(target=self.recieveStream, args=(conn, askedStream))
                thread.start()
            evento.clear()

    def updateVideoList(self, mensagem, evento):
        vids = mensagem.split('-ADD-')
        vids.pop()
        for video in vids:
            stream = Stream(video, evento, self.caminhos)
            self.streamList.append(stream)
    
    def checkWhatStream(self):
        for stream in self.streamList:
            if Stream.getStatus(stream) ==  "Pending":
                return stream
        return None
    
    def recieveStream(self, conn, sStream):
        i = 0
        while True:
            print("Frame: ", i)
            #parse packet | Recebe o tamanho do frame (4 bytes) do servidor
            allpacket_size = conn.recv(4)
            packet_size = int.from_bytes(allpacket_size, byteorder='big')
            
            # Recebe o pacote do servidor
            pacote= b""
            pacote += allpacket_size
            while len(pacote) < packet_size+4:
                pacote += conn.recv(packet_size+4 - len(pacote))

            #Enviar o pacote a todos os clientes
            Stream.sendStream(sStream)
            i+=1
            '''

class RPGUI:

    def __init__(self, file):
        #self.IP = getIP
        self.IP = '127.0.0.1'
        self.PORTACLIENT = None
        self.PORTASERVER = None
        self.socketForServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketForClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.streamList = []
        self.caminhos = ["127.0.0.4 <- 127.0.0.3 <- 127.0.0.2"]
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
            cliente = Cliente(conn, addr)
            askedStream = cliente.initialClientConn(self.streamList)
            if askedStream:
                for stream in self.streamList:
                    if askedStream == Stream.getName(stream):
                        Stream.addClient(cliente.ip)
                        break
        except Exception as e:
            print(f"Erro no processamento do cliente{addr[0]}: {e}")
        finally:
            conn.close()
            del cliente

    #-----------------------------------------------------------------------------------------
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
            servidor = Server(conn, addr)
            servidor.initialServerConnection()
        finally:
            conn.close()
    

if __name__ == "__main__":
    try:
        filename = "config_file.txt"
        # Criar um RP
        rp = RPGUI(filename)
    except:
        print("[Usage: RP.py]\n")	