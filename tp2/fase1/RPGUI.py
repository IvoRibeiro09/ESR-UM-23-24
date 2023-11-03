import socket
import threading
import tkinter as tk
from auxiliarFunc import *

class RPGUI:

    def __init__(self, file):
        #self.IP = getIP
        self.IP = '127.0.0.1'
        self.PORTACLIENT = None
        self.PORTASERVER = None
        self.socketForServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketForClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.streamList = []
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
    '''import socket

def server_function(port):
    # Crie um socket do servidor
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Associe o servidor ao endereço e à porta
    server_address = ('', port)
    server_socket.bind(server_address)
    
    # Comece a ouvir por conexões de clientes
    server_socket.listen(1)
    print(f"Servidor está ouvindo na porta {port}")
    
    while True:
        # Espere por uma conexão de cliente
        print("Aguardando conexão de um cliente...")
        client_socket, client_address = server_socket.accept()
        print(f"Conexão recebida de {client_address}")
        
        try:
            # Receba os dados do cliente
            data = client_socket.recv(1024)
            message = data.decode()
            
            # Verifique se a mensagem é "VideoList"
            if message == "VideoList":
                # Simule uma lista de vídeos no servidor
                lista_de_videos = "video1.mp4, video2.mp4, video3.mp4"
                
                # Envie a lista de vídeos de volta ao cliente
                client_socket.sendall(lista_de_videos.encode())
                print("Lista de vídeos enviada ao cliente")
            else:
                print("Mensagem não reconhecida:", message)
        except Exception as e:
            print("Erro durante a comunicação com o cliente:", str(e))
        finally:
            # Feche o socket do cliente
            client_socket.close()

# Exemplo de uso: Inicie o servidor na porta 12345
server_function(12345)
'''
    
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
        filename = "config_file.txt"
        # Criar um RP
        rp = RPGUI(filename)
    except:
        print("[Usage: RP.py]\n")	