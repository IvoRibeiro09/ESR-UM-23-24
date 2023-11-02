import tkinter as tk
import socket

class ClienteGUI:

    def __init__(self, ip, node):
        #self.janela = janela
        self.IP = ip
        self.porta= 12345
        self.adjacentes = node
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_address = (node, self.porta)
        self.StreamPause = False
        self.videosNoRP = None
        #self.parse()
        self.clientStart()

    def parse(self, file):
        with open(file, 'r') as f:
            for line in f:
                if self.IP in line:
                    while "#####" not in line:
                        print("parse estas proximas linhas")


    def clientStart(self):
        #conectar ao servidor 
        self.server_socket.connect(self.socket_address)
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
        ip = '127.0.0.3'
        portaClient = 12345
        ip_rp = '127.0.0.1'

        # Criar um cliente
        #janela = tk()
        cliente = ClienteGUI(ip, ip_rp)
        # cliente.parse(file)
        #cliente.clientStart()
        #cliente.janela.title("Servidor")
        #janela.mainloop()
    except Exception as e:
        print(f"Erro: {e}")
        print("[Usage: Cliente.py]\n")