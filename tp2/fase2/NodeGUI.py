import threading
import socket
from auxiliarFunc import *

class NodeGUI:
    def __init__(self, ip, file):
        self.janela = None
        self.IP = ip
        self.portaEscuta = None
        self.adjacentes = []
        self.parse(file)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.IP, self.portaEscuta))
        self.start()

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
                    elif "neighbour- " in line:
                        self.adjacentes.append(extrair_neighbour(line))
                    elif "nodePort- " in line:
                        self.portaEscuta = extrair_numero_porta(line)

    def start(self):
        # ter uma janela que ao ligar tem as opçoes testar conexao e espera o clique para cemçar a testar
        # iniciar a thread que receve conexoes que so ira ser fechada quando clicar em close
        # iniciar o connection test qunado clicar no botao start teste connection
        thread0 = threading.Thread(target=self.recieveConnection)
        thread1 = threading.Thread(target=self.connectionTest)
        thread0.start()
    
    def connectionTest(self):
        msg = self.IP
        self.sendMessageToAdjacentNodes(msg)

    def recieveConnection(self):
        #uma thread a receber conexoes
        #quando recebe verifica se o seu nome nao esta presente 
        # se estiver nao faz nada
        # se nao estiver mete o seu ip na mesnagem e envia aos seus visinhos
        while self.server_socket:
            try:
                client_connection, client_address = self.server_socket.accept()
                print(f"Node {client_address[0]} send connection test to: {self.IP}")

                size = self.server_socket.recv(4)
                msg_size = int.from_bytes(size, byteorder='big')
                
                msg = b""
                while len(msg) < msg_size:
                    msg += self.server_socket.recv(msg_size - len(msg)) 
                
                mensagem = msg.decode('utf-8')

                if self.IP not in mensagem:
                    mensagem = mensagem + " -> " + self.IP
                    self.sendMessageToAdjacentNodes(mensagem)

            except Exception as e:
                print(f"Erro na receção de conexões no Nodo {self.IP}")
                
    def sendMessageToAdjacentNodes(self, mensagem):
        for adj in self.adjacentes:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((adj[1], int(adj[2])))

                msg = (
                    len(mensagem).to_bytes(4, 'big') +
                    mensagem.encode('utf-8')
                )
                s.sendall(msg)
               
                s.close()
            except Exception as e:
                print("Não foi possivel enviar mensagem")


if __name__ == "__main__":
    try:
        # Obtém o endereço IP local da máquina
        ip = input("IP da maquina atual:")
        filename = "config_file.txt"
        print(ip)
        filename = "config_file.txt"
        node = NodeGUI(ip, filename)
        #node.janela.mainloop()

    except Exception as e:
        print(f'Ocorreu um erro: {str(e)}')