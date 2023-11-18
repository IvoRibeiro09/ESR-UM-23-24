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
        socket_address = (NodeData.getIp(self.node), NodeData.getNodePort(self.node))
        print(f"{NodeData.getIp(self.node)} waiting for Node connections")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(socket_address)
            server_socket.listen()
            while True:
                try:
                    client_connection, _ = server_socket.accept()
                    #client_connection.settimeout(60)  # Defina o timeout para o recebimento de dados

                    size = client_connection.recv(4)
                    msg_size = int.from_bytes(size, byteorder='big')

                    msg = b""
                    while len(msg) < msg_size:
                        msg += client_connection.recv(msg_size - len(msg))

                    mensagem = msg.decode('utf-8')

                    if NodeData.getIp(self.node) not in mensagem:
                        mensagem = mensagem + " <- " + NodeData.getIp(self.node) + " | " + NodeData.getIp(self.node)
                        self.sendMessageToAdjacentNodes(mensagem)

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

    #-----------------------------------------------------------------------------------------
    # Receber de Streams e enviar
    def streamConnection(self):
        my_address = (NodeData.getIp(self.node), NodeData.getStreamPort(self.node))
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as socketForStream:
            try:
                socketForStream.bind(my_address)
                print(f"{my_address} waiting for Streams")
                while True:
                    #parse packet
                    data, _ = socketForStream.recvfrom(Packet_size)
                    
                    pck = Packet("","", "")
                    pck.parsePacket(data)
                    caminhos = []
                    extrair_conexoes(caminhos, pck.info)
                    
                    #e enviar para todos os clientes
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as stream_socket:
                        try:
                            for nei in caminhos:
                                print("caminhos: ", nei)
                                pckToSend = Packet(nei[1],pck.frameNumber, pck.frame)
                                dataToSend = pckToSend.buildPacket()
                                send_address = (nei[0], Node_Port)
                                stream_socket.sendto(dataToSend, send_address)
                        except Exception as e:
                            print(f"Error sending stream from Node{NodeData.getIp(self.node)}: {e}")
                        finally:
                            stream_socket.close()                   
            except Exception as e:
                print(f"Erro no streaming no Nó {NodeData.getIp(self.node)}: {e}")
            finally:
                socketForStream.close()