import tkinter as tk
import socket
from auxiliarFunc import *
class ClienteGUI:

    def __init__(self, file):
        #self.janela = janela
        #self.IP = getIP
        self.IP = '127.0.0.3'
        self.adjacentes = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.StreamPause = False
        self.videosNoRP = None
        self.parse(file)
        self.clientStart()

    
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
        
    def clientStart(self):
        #conectar ao servidor 
        socket_address = self.adjacentes[0]
        self.server_socket.connect(socket_address)
        print("Conectado ao RP")
        #pedir os videos que ele tem 
        print("Pedido de quais videos exixtem no RP enviado")
        message = "VideoList"
        self.server_socket.sendall((message).encode())
        #receber a lista de video do rp
        data = self.server_socket.recv(1024)
        decodedData = str(data)[2:-1]
        print('Videos presentes no RP:',decodedData)

        print("Pedido de quais videos exixtem no RP recebido")
        print(self.videosNoRP)
    '''import socket

def comunicar_com_client(client_instance, server_address):
    # Criar um socket de cliente
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Conectar ao servidor
        client_socket.connect(server_address)
        print("Conectado ao servidor RP")

        # Enviar pedido de lista de vídeos
        message = "VideoList"
        client_socket.sendall(message.encode())
        print("Pedido de lista de vídeos enviado")

        # Receber a lista de vídeos do servidor
        data = client_socket.recv(1024)
        decoded_data = data.decode()
        print('Videos presentes no servidor RP:', decoded_data)

    except Exception as e:
        print("Erro durante a comunicação com o servidor:", str(e))
    finally:
        # Fechar o socket do cliente
        client_socket.close()

# Suponha que você tenha um objeto 'cliente' e o endereço do servidor (host, porta) apropriado.
# Substitua 'server_address' pelo endereço real do servidor que você deseja se conectar.
server_address = ('localhost', 12345)  # Exemplo: ('localhost', 12345)

# Chame a função para comunicar com o cliente
comunicar_com_client(client_instance=cliente, server_address=server_address)
'''

    def clienteInterface2(self): 
        # Butao streamar e enviar a stream de video para o cliente		
        self.botaoStart = tk.Button(self.janela, width=20, padx=3, pady=3)
        self.botaoStart["text"] = "Play"
        self.botaoStart["command"] = self.playStream
        self.botaoStart.grid(row=0, column=1, padx=2, pady=2)
        
        # Butao pausa de enviar a stream de video para o cliente				
        self.botaoPause = tk.Button(self.janela, width=20, padx=3, pady=3)
        self.botaoPause["text"] = "Pause"
        self.botaoPause["command"] = self.pauseStream
        self.botaoPause.grid(row=0, column=2, padx=2, pady=2)
            
        # Para de streamar o video
        self.botaoClose = tk.Button(self.janela, width=20, padx=3, pady=3)
        self.botaoClose["text"] = "Close"
        self.botaoClose["command"] =  self.exitClient
        self.botaoClose.grid(row=0, column=3, padx=2, pady=2)

    def playStream(self, video):
        #pedir stream ao RP
        print("Pedido de envio do video "+video+ " ao servidor "+ self.socket_address)
        #receber os dados
        print("A receber video")


if __name__ == "__main__":
    try:
        filename = "config_file.txt"

        # Criar um cliente
        #janela = tk()
        cliente = ClienteGUI(filename)
        # cliente.parse(file)
        #cliente.clientStart()
        #cliente.janela.title("Servidor")
        #janela.mainloop()
    except Exception as e:
        print(f"Erro: {e}")
        print("[Usage: Cliente.py]\n")