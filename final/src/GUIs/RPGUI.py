import socket
import threading
import tkinter as tk
from src.auxiliarFunc import *
from src.Stream import *
from src.NodeData import *
from src.Packet import *

'''
Esta é a classe principal para o RendezvousPoint
'''
class RPGUI:
    def __init__(self, node):
        self.node = node
        self.clients_logged = {}
        self.streamList = {}
        self.caminhos = []
        self.janela = None
        self.condition = threading.Condition()
        self.conditionBool = False
        self.startRP()

    def startRP(self):
        print("Starting...")
        thread0 = threading.Thread(target=self.NodeConnection)
        thread1 = threading.Thread(target=self.clientConnection)
        thread2 = threading.Thread(target=self.serverConnection)
        thread3 = threading.Thread(target=self.streamConnection)
        thread0.start()
        thread1.start()
        thread2.start()
        thread3.start()

    #-----------------------------------------------------------------------------------------
    # Tratamento de Nós
    def NodeConnection(self):
        thread = threading.Thread(target=self.startNetwork)
        thread.start()
        self.recieveNodeConnection()

    # Metodo que cria uma interface grafica que permite ao RP construir a rede apos selecionar essa 
    # opção indicada
    # esta funcionalidade permite garantir que a rede so é estabelecida depois de todos os nodos estiverem ligados
    # apos selecionada é enviada a mensagem de "Start Network" aos nodos vizinhos que iram fazer o mesmo para os seus
    # vizinhos que depois iniciaram a construção da rede no sentido inverso
    def startNetwork(self):
        self.janela = tk.Tk()
        self.janela.title(f'RendezvousPoint: {NodeData.getIp(self.node)}')
        self.label = tk.Label(self.janela, width=60, padx=10, pady=10)
        self.label["text"] = "Deseja construir a rede overlay?"
        self.label.grid(row=0, column=0, padx=10, pady=10)	
        self.botaoStart = tk.Button(self.janela, width=30, padx=10, pady=10)
        self.botaoStart["text"] = "Start"
        self.botaoStart["command"] = self.startTest
        self.botaoStart.grid(row=1, column=0, padx=10, pady=10)
        self.janela.mainloop()

        with self.condition:
            while not self.conditionBool:
                self.condition.wait()
        self.conditionBool = False

        try:
            msg = "Start Network"
            msg_data = (
                len(msg).to_bytes(4, 'big') +
                msg.encode('utf-8')
            )
            for node in NodeData.getNeighboursAddress(self.node):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as node_starter_socket:      
                        node_adress = (node, NodeData.getNodePort(self.node))
                        node_starter_socket.connect(node_adress)
                        node_starter_socket.sendall(msg_data)
                except Exception:
                    print("Erro ao enviar mensagem de iniciar a rede para o no: ", node)
                finally:
                    node_starter_socket.close()
        except Exception as e:
            print("Erro ao iniciar a rede overlay: ", e)
        finally:
            node_starter_socket.close()

    def startTest(self):
        with self.condition:
            self.conditionBool = True
            self.condition.notify()
        self.janela.destroy()
        
    # Metodo responsavel por receber os caminhos provenientes de todos os nodos e inverte-os por virem 
    # no sentido contrario e guarda essa informação construindo assim a rede overlay
    def recieveNodeConnection(self):
        socket_address = (NodeData.getIp(self.node), NodeData.getNodePort(self.node))
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as node_socket:
                node_socket.bind(socket_address)
                node_socket.listen(1)
                print("RP waiting for Node connections: ", socket_address)
                while True:
                    client_connection,_ = node_socket.accept()

                    size = client_connection.recv(4)
                    msg_size = int.from_bytes(size, byteorder='big')

                    msg_data = client_connection.recv(msg_size)
                    mensagem = msg_data.decode('utf-8')
                    
                    if "Start Network" not in mensagem:
                        mensagem = mensagem + " <- " + NodeData.getIp(self.node)
                        cam = inverter_relacoes(mensagem)
                        print("New connection: " + cam)
                        self.caminhos.append(cam)
                        client_connection.close()

        except Exception as e:
            print(f"Erro na receção dos caminhos para os Nós no RP: ",e)
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
                    thread = threading.Thread(target=self.initialClientConn, args=(conn, addr))
                    thread.start()
            finally:
                socketForClient.close()
    
    # Metodo que trata de receber as conexões de clientes e consuante a sua escolhade stream
    # trata de os adicionar à Stream indicada 
    # tambem quando um cliente decide deixar de assitir uma stream trata de o remover dessa stream
    # e avisa ainda o servidor no caso de não exitir nenhum cliente a assistir 
    def initialClientConn(self, conn, addr):
        try:
            mensagem = conn.recv(1024).decode()

            if mensagem == "VideoList":
                print(f"Client {addr} connected!")
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
                    stream = self.streamList[selectedStream]
                    self.clients_logged[addr[0]] = selectedStream
                    
                    Stream.addClient(stream, addr[0], self.caminhos)
                    print(f"Client {addr} added to Stream {selectedStream}")

            elif mensagem == "Connection closed":
                stream_do_cliente = self.clients_logged[addr[0]]
                stream = self.streamList[stream_do_cliente]
                Stream.rmvClient(stream, addr[0])
                # avisar o Server para parar de stremar
                if Stream.getStatus(stream) == "Closed":
                    server_address = (Stream.getServerAddress(stream)[0], NodeData.getPortaServer(self.node))
                    print(server_address)
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_server:
                        socket_server.connect((Stream.getServerAddress(stream)[0],NodeData.getPortaServer(self.node)))

                        mensagem = f"Stop Stream- {stream_do_cliente}"
                        socket_server.send(mensagem.encode('utf-8'))
                        
                        socket_server.close()
                
                del self.clients_logged[addr[0]]
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
    
    # Metodo que trata de receber conexões de servidores e as suas listas de streams
    # para cada stream que o servidor é capaz de transmitir é criada uma estrutura stream
    # com a informação do servidor que tem essa stream assim como o seu nome 
    def initialServerConnection(self, conn, addr):
        try:
            # receber mensagens com a lista das streams
            data = conn.recv(1024)
            mensagem = data.decode('utf-8')
            lista_de_videos = mensagem.split('-AND-')
            
            # Cria uma Stream por transmissao de cada servidor
            for videoname in lista_de_videos:
                stream = Stream(videoname, NodeData.getNodePort(self.node), (addr[0],NodeData.getPortaServer(self.node)))
                self.streamList[stream.name] = stream
            
            print(f'Stream list updated with: {lista_de_videos}')
        except Exception as e:
            print(f"Erro no processamento do servidor {addr[0]}: {e}")
        
    #-----------------------------------------------------------------------------------------
    # Receber de Streams e enviar

    # Metodo responsavel por lidar com as mensagens de transmissão de frame do servidor para os respetivos
    # clientes seguindo o caminho previamente definido 
    # recebe o pacote com o nome da stream e consuante esse nome refaz o pacote com o caminho a percorrer
    # e envia para o respectivo nodo vizinho nesse caminho
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