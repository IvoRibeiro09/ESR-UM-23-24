import socket
from auxiliarFunc import *
from NodeData import *

class NodeRPGUI:

    def __init__(self, node):
        self.janela = None
        self.node = node
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nodeState = True
        self.caminhos = []
        self.start()

    def start(self):
        print("Starting...")
        socket_address = (NodeData.getIp(self.node), NodeData.getPortaEscuta(self.node))
        self.server_socket.bind(socket_address)
        self.server_socket.listen()
        while self.nodeState:
            client_connection, client_address = self.server_socket.accept()
    
            size = client_connection.recv(4)
            msg_size = int.from_bytes(size, byteorder='big')
                    
            msg = b""
            while len(msg) < msg_size:
                msg += client_connection.recv(msg_size - len(msg))
                    
            mensagem = msg.decode('utf-8')
            print(mensagem)
            self.caminhos.append(mensagem)

    def printCaminhos(self):
        for caminho in self.caminhos:
            print(caminho)