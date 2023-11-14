import socket
import threading
from auxiliarFunc import *
from Stream import *
from NodeData import *
from Packet import *
BUFFER_SIZE = 110000

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
            socketForClient.listen(1)
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

            for stream in self.streamList:
                if Stream.getName(stream) == selectedStream:
                    Stream.addClient(stream, addr[0])
                    break

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
            
            for videoname in lista_de_videos:
                stream = Stream(videoname,('127.0.0.2',NodeData.getPortaServer(self.node)), self.caminhos)
                self.streamList.append(stream)
            
            print(f'Videos disponíveis: {lista_de_videos}')
        except Exception as e:
            print(f"Erro no processamento do servidor {addr[0]}: {e}")
        
    #-----------------------------------------------------------------------------------------
    # Receber de Streams e enviar
    def streamConnection(self):
        socket_address = (NodeData.getIp(self.node), NodeData.getStreamPort(self.node))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketForStream:
            try:
                #socketForStream.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, BUFFER_SIZE)
                socketForStream.bind(socket_address)
                print("RP à espera de conexões de Streams: ", socket_address)
                i=0
                while True:
                    #parse packet | Recebe o tamanho do frame (4 bytes) do servidor
                    allpacket_size = socketForStream.recv(4)
                    print("Frame: ", i)
                    packet_size = int.from_bytes(allpacket_size, byteorder='big')
                    
                    # Recebe o pacote do servidor
                    pacote_data = b""
                    pacote_data += allpacket_size
                    while len(pacote_data) < packet_size + 4:
                        pacote_data += socketForStream.recv(packet_size + 4 - len(pacote_data))

                    pacote = Packet()
                    Packet.parsePacket(pacote, pacote_data)

                    stream_track = ""
                    for stream in self.streamList:
                        if Stream.getName(stream) == Packet.getName(pacote):
                            stream_track = Stream.getCaminhoDaStream(stream)
                    
                    # descubrir quais os nodos para onde tem de enviar
                    nodesToSend = []
                    nodesToSend.append("127.0.0.3")
                    # contruir o pacote com o resto do caminho
                    tracked_packet = TrackedPacket.buildTrackedPacket(pacote, stream_track)
                    # Enviar para todos os nós que estão na lista de envio
                    for node in nodesToSend:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as stream_socket:
                            try:
                                stream_socket.sendto(tracked_packet, (node,NodeData.getStreamPort(self.node)))
                            except Exception as e:
                                print(f"Erro a enviar a Stream a partir do RP: {e}")
                            finally:
                                stream_socket.close()
                    i+=1

            except Exception as e:
                print(f"Erro no processamento da Stream no RP: {e}")
            finally:
                socketForStream.close()