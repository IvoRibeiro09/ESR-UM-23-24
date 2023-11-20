import socket
import threading
from auxiliarFunc import *
from Stream import *
from NodeData import *
from Packet import *

class RPGUI:

    def __init__(self, node):
        self.node = node
        self.clients_logged = {}
        self.streamList = {}
        self.caminhos = []
        self.startRP()

    def startRP(self):
        print("Starting...")
        thread0 = threading.Thread(target=self.recieveNodeConnection)
        thread1 = threading.Thread(target=self.clientConnection)
        thread2 = threading.Thread(target=self.serverConnection)
        thread3 = threading.Thread(target=self.streamConnection)
        thread0.start()
        thread1.start()
        thread2.start()
        thread3.start()

    #-----------------------------------------------------------------------------------------
    # Tratamento de Nós
    def recieveNodeConnection(self):
        socket_address = (NodeData.getIp(self.node), NodeData.getNodePort(self.node))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as node_socket:
            node_socket.bind(socket_address)
            node_socket.listen(1)
            print("RP waiting for Node connections: ", socket_address)
            try:
                while True:
                    client_connection,_ = node_socket.accept()

                    size = client_connection.recv(4)
                    msg_size = int.from_bytes(size, byteorder='big')

                    msg = b""
                    while len(msg) < msg_size:
                        msg += client_connection.recv(msg_size - len(msg))

                    mensagem = msg.decode('utf-8')
                    mensagem = mensagem + " <- " + NodeData.getIp(self.node)
                    cam = inverter_relacoes(mensagem)
                    print("New connection: " + cam)
                    self.caminhos.append(cam)
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
            socketForClient.listen(1)
            print("RP waiting for Client connections: ", socket_address)
            try:
                while True:
                    conn, addr = socketForClient.accept()
                    print(f"Client {addr} connected!")
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
                    for stream in self.streamList.keys():
                        msg += stream+"/"    
                    conn.sendall(msg.encode())
            
                    recv_msg = conn.recv(1024).decode()
                    selectedStream = extrair_texto(recv_msg)

                    print(f"Client {addr[0]} ask for stream: {selectedStream}")

                    stream = self.streamList[selectedStream]
                    self.clients_logged[addr[0]] = selectedStream
                    print(self.clients_logged)
                    Stream.addClient(stream, addr[0], self.caminhos)

            elif mensagem == "Connection closed":
                stream_do_cliente = self.clients_logged[addr[0]]
                stream = self.streamList[stream_do_cliente]
                Stream.rmvClient(stream, addr[0])
                # avisar o Server para parar de stremar
                print(f"Client {addr[0]} disconnected.")

        except Exception as e:
            print(f"Erro no processamento do cliente {addr[0]}: {e}")
        finally:
            conn.close()

    #-----------------------------------------------------------------------------------------
    # Tratamento de Servidores
    def serverConnection(self):
        socket_address = (NodeData.getIp(self.node), NodeData.getPortaServer(self.node))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketForServer:
            socketForServer.bind(socket_address)
            socketForServer.listen(1)
            print("RP waiting for Server connections: ", socket_address)
            try:
                while True:
                    conn, addr = socketForServer.accept()
                    print(f"Server {addr} connected!")
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
            lista_de_videos = mensagem.split('-AND-')
            
            for videoname in lista_de_videos:
                stream = Stream(videoname,(addr[0],NodeData.getPortaServer(self.node)))
                self.streamList[stream.name] = stream
            
            print(f'Stream list updated with: {lista_de_videos}')
        except Exception as e:
            print(f"Erro no processamento do servidor {addr[0]}: {e}")
        
    #-----------------------------------------------------------------------------------------
    # Receber de Streams e enviar
    def streamConnection(self):
        my_address = (NodeData.getIp(self.node), NodeData.getStreamPort(self.node))
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as socketForStream:
            try:
                socketForStream.bind(my_address)
                print("RP waiting for Stream connections: ", my_address)
                while True:
                    data, _ = socketForStream.recvfrom(Packet_size)
                    
                    # Parse the packet using your Packet class
                    received_packet = Packet("", "", "")
                    received_packet.parsePacket(data)
                    stream = self.streamList[received_packet.info]
                    
                    Stream.sendStream(stream, received_packet.frameNumber, received_packet.frame)
            except Exception as e:
                print(f"Error in streamConnection: {e}")
            finally:
                socketForStream.close()                