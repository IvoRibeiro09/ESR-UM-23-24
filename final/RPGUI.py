import socket
import threading
from auxiliarFunc import *
from Stream import *
from NodeData import *

class RPGUI:

    def __init__(self, node):
        self.node = node
        self.streamList = []
        self.caminhos = []
        self.startRP()

    def startRP(self):
        print("Starting...")
        thread0 = threading.Thread(target=self.recieveNodeConnection)
        thread1 = threading.Thread(target=self.clientConnection)
        thread2 = threading.Thread(target=self.serverConnection)
        thread0.start()
        thread1.start()
        thread2.start()

    #-----------------------------------------------------------------------------------------
    # Tratamento de Nós
    def recieveNodeConnection(self):
        socket_address = (NodeData.getIp(self.node), NodeData.getNodePort(self.node))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as node_socket:
            node_socket.bind(socket_address)
            node_socket.listen()
            print("RP à espera dos caminhos para os nós: ", socket_address)
            try:
                while True:
                    client_connection,_ = node_socket.accept()

                    size = client_connection.recv(4)
                    msg_size = int.from_bytes(size, byteorder='big')

                    msg = b""
                    while len(msg) < msg_size:
                        msg += client_connection.recv(msg_size - len(msg))

                    mensagem = msg.decode('utf-8')
                    print("caminho: " + mensagem)
                    self.caminhos.append(mensagem)
                    client_connection.close()
            except Exception as e:
                print(f"Erro na receção de conexões no Nodo {NodeData.getIp(self.node)}")
            finally:
                node_socket.close()

    #-----------------------------------------------------------------------------------------
    # Tratamento de Clientes
    def clientConnection(self):
        socket_address = (NodeData.getIp(self.node), NodeData.getPortaClient(self.node))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketForClient:
            socketForClient.bind(socket_address)
            socketForClient.listen()
            print("RP à espera de conexão de Clientes: ", socket_address)
            try:
                while True:
                    conn, addr = socketForClient.accept()
                    print(f"Cliente {addr} conectado!")
                    thread = threading.Thread(target=self.initialClientConn, args=(conn, addr))
                    thread.start()
            finally:
                socketForClient.close()
   
    def initialClientConn(self, conn, addr):
        try:
            mensagem = conn.recv(1024).decode()

            if mensagem == "VideoList":
                # Envie a lista de vídeos de volta ao cliente
                if not self.streamList:
                    noVidmsg = "I DONT HAVE STREAMS"
                    conn.sendall(noVidmsg.encode())
                else:
                    msg = ""
                    for stream in self.streamList:
                        msg = msg+f"{Stream.getName(stream)}/"    
                    conn.sendall(msg.encode())
                print("Lista de vídeos enviada ao cliente: ",addr[0])
            else:
                print("Mensagem não reconhecida:", mensagem)
                return None
            recv_msg = conn.recv(1024).decode()
            selectedStream = extrair_texto(recv_msg)

            print(f"Cliente {addr[0]} pediu a visualização da stream: {selectedStream}")
            return selectedStream
        except Exception as e:
            print(f"Erro no processamento do cliente {addr[0]}: {e}")
            return None
        finally:
            conn.close()

    #-----------------------------------------------------------------------------------------
    # Tratamento de Servidores
    def serverConnection(self):
        socket_address = (NodeData.getIp(self.node), NodeData.getPortaServer(self.node))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketForServer:
            socketForServer.bind(socket_address)
            socketForServer.listen()
            print("RP à espera de conexões de Servidores: ", socket_address)
            try:
                while True:
                    conn, addr = socketForServer.accept()
                    print(f"Servidor {addr} conectado!")
                    thread = threading.Thread(target=self.initialServerConnection, args=(conn, addr))
                    thread.start()
            finally:
                socketForServer.close()

    def initialServerConnection(self, conn, addr):
        try:
            # perguntar quais os videos que o servidor tem para transmitir
            # receber mensagens com o nome dos videos
            data = conn.recv(1024)
            mensagem = data.decode('utf-8')
            # Processar e responder às mensagens recebidas aqui
            lista_de_videos = mensagem.split('-ADD-')
            vids = lista_de_videos.pop()
            
            for videoname in vids:
                stream = Stream(videoname, addr, self.caminhos)
                self.streamList.append(stream)
            
            print(f'Videos disponíveis: {self.streamList}')
        except Exception as e:
            print(f"Erro no processamento do servidor {addr[0]}: {e}")
            return None
        finally:
            conn.close()