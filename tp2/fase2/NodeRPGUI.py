import socket
from auxiliarFunc import *

class NodeRPGUI:
    def __init__(self, ip, file):
        self.janela = None
        self.IP = ip
        self.portaEscuta = None
        self.adjacentes = []
        self.parse(file)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nodeState = True
        self.caminhos = []
        self.start()

    def parse(self, file):
        print("Parsing...")
        try:
            with open(file, 'r') as f:
                read = False
                for line in f:
                    if f"ip- {self.IP}" in line:
                        read = True
                    if read:
                        if "neighbour- " in line:
                            self.adjacentes.append(extrair_texto_numero(line))
                        elif "nodePort- " in line:
                            self.portaEscuta = extrair_numero(line)
                        elif "------" in line:
                            break
        except FileNotFoundError:
            print(f"Error: File '{file}' not found.")
        except Exception as e:
            print(f"An error occurred during parsing: {str(e)}")

    def start(self):
        print("Starting...")
        socket_address = (self.IP, self.portaEscuta)
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

if __name__ == "__main__":
    try:
        # Obtém o endereço IP local da máquina
        ip = str(input("IP da maquina atual:"))
        filename = "config_file.txt"
        print(ip)
        noderp = NodeRPGUI(ip, filename)

    except Exception as e:
        print(f'Ocorreu um erro: {str(e)}')