import threading
import socket
import time
import tkinter as tk
from NodeData import *
from Packet import *

class NodeGUI:

    def __init__(self, node):
        self.janela = None
        self.node = node
        self.condition = threading.Condition()
        self.conditionBool = False
        self.start()

    def start(self):
        print("Starting...")
        # ter uma janela que ao ligar tem as opçoes testar conexao e espera o clique para cemçar a testar
        # iniciar a thread que receve conexoes que so ira ser fechada quando clicar em close
        # iniciar o connection test qunado clicar no botao start teste connection
        thread0 = threading.Thread(target=self.recieveConnection)
        thread1 = threading.Thread(target=self.connectionTest)
        thread0.start()
        thread1.start()
        thread1.join()
        if NodeData.getType(self.node) == "Node":
            thread2 = threading.Thread(target=self.streamConnection)
            thread2.start()

    def connectionTest(self):
        self.janela = tk.Tk()
        self.janela.title(f'Node: {NodeData.getIp(self.node)}')
        print("Show interface1...")
       
        spacing = 10
        #tela com nome
        self.label = tk.Label(self.janela, width=60, padx=spacing, pady=spacing)
        self.label["text"] = "Deseja iniciar o teste de conexão deste nodo?"
        self.label.grid(row=0, column=0, padx=spacing, pady=spacing)

        # Botao streamar e enviar a stream de video para o cliente		
        self.botaoStart = tk.Button(self.janela, width=30, padx=spacing, pady=spacing)
        self.botaoStart["text"] = "Start"
        self.botaoStart["command"] = self.startTest
        self.botaoStart.grid(row=1, column=0, padx=spacing, pady=spacing)
        self.janela.mainloop()

        with self.condition:
            while not self.conditionBool:
                self.condition.wait()
        self.conditionBool = False

        msg = NodeData.getIp(self.node)
        self.sendMessageToAdjacentNodes(msg)
        print("Connection test done!")

    def startTest(self):
        with self.condition:
            self.conditionBool = True
            self.condition.notify()
        self.janela.destroy()

    def recieveConnection(self):
        #uma thread a receber conexoes
        #quando recebe verifica se o seu nome nao esta presente 
        # se estiver nao faz nada
        # se nao estiver mete o seu ip na mesnagem e envia aos seus visinhos
        print("Recieving...")
        socket_address = (NodeData.getIp(self.node), NodeData.getNodePort(self.node))

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(socket_address)
            server_socket.listen()
            while True:
                try:
                    client_connection, _ = server_socket.accept()
                    client_connection.settimeout(60)  # Defina o timeout para o recebimento de dados

                    size = client_connection.recv(4)
                    msg_size = int.from_bytes(size, byteorder='big')

                    msg = b""
                    while len(msg) < msg_size:
                        msg += client_connection.recv(msg_size - len(msg))

                    mensagem = msg.decode('utf-8')

                    if NodeData.getIp(self.node) not in mensagem:
                        mensagem = mensagem + " <- " + NodeData.getIp(self.node)
                        self.sendMessageToAdjacentNodes(mensagem)

                except socket.timeout:
                    print(f"Nenhum cliente conectou-se ao Node {NodeData.getIp(self.node)} dentro do tempo limite. Parando a receção de conexões.")
                    break
                except Exception as e:
                    print(f"Erro na receção de conexões no Nodo {NodeData.getIp(self.node)}")

    def sendMessageToAdjacentNodes(self, mensagem):
        for adj in NodeData.getNeighboursAddress(self.node): 
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((adj, NodeData.getNodePort(self.node)))

                    msg = (
                        len(mensagem).to_bytes(4, 'big') +
                        mensagem.encode('utf-8')
                    )
                    s.sendall(msg)
                
            except Exception as e:
                print(f"Não foi possível enviar mensagem para {adj[0]}:{adj[1]}. Erro: {str(e)}")
            finally:
                # Certifique-se de que a conexão seja fechada mesmo em caso de exceção
                s.close()

    def connectionVerify(self):
        time.sleep(30)
        msg = NodeData.getIp(self.node)
        self.sendMessageToAdjacentNodes(msg)
        print("Connection test done!")

    #-----------------------------------------------------------------------------------------
    # Receber de Streams e enviar
    def streamConnection(self):
        my_address = (NodeData.getIp(self.node), NodeData.getStreamPort(self.node))
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as socketForStream:
            try:
                socketForStream.bind(my_address)
                print(f"{my_address} à espera de conexões de Streams: ")
                i=0
                while True:
                    #parse packet | Recebe o tamanho do frame (4 bytes) do servidor
                    allpacket_size, _ = socketForStream.recvfrom(4)
                    print("Frame: ", i)
                    i += 1
                    packet_size = int.from_bytes(allpacket_size, byteorder='big')
                    
                    # Recebe o pacote do servidor
                    pacote_data = b""
                    pacote_data += allpacket_size
                    while len(pacote_data) < packet_size + 4:
                        data, _ = socketForStream.recvfrom(packet_size + 4 - len(pacote_data))
                        pacote_data += data
                    '''
                    pacote = Packet()
                    Packet.parsePacket(pacote, pacote_data)
                    msgToSend = Packet.buildPacket(pacote)
                    '''
                    my_address = (NodeData.getIp(self.node), 0)
                    for node in NodeData.getNeighboursAddress(self.node):
                        if node != '127.0.0.1':
                            send_address = (node, 22222)
                            print("Send to: ", send_address)
                            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as stream_socket:
                                try:
                                    stream_socket.bind(my_address)
                                    stream_socket.sendto(pacote_data, send_address)
                                except Exception as e:
                                    print(f"Erro na Stream a partir do {NodeData.getIp(self.node)}: {e}")
                                finally:
                                    stream_socket.close()
            except Exception as e:
                print(f"Erro no streaming no Nó{NodeData.getIp(self.node)}: {e}")
            finally:
                socketForStream.close()