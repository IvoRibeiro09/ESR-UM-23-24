import tkinter as tk
import socket
from auxiliarFunc import *
import threading

class ClienteGUI:

    def __init__(self, file):
        self.janela = None
        #self.IP = getIP
        self.IP = '127.0.0.3'
        self.adjacentes = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.streansNoRP = None
        self.condition = threading.Condition()
        self.streamSelected = None
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
        print("Starter...")
        self.inicialConnection()
        self.askStreamTransmission()
        self.streamTransmission()
        self.server_socket.close()

    def inicialConnection(self):
        #conectar ao servidor 
        socket_address = self.adjacentes[0]
        self.server_socket.connect(socket_address)
        #pedir os videos que ele tem 
        try:
            message = "VideoList"
            self.server_socket.sendall((message).encode())
            #receber a lista de video do rp
            data = self.server_socket.recv(1024)
            mensagem = data.decode()
            vids = mensagem.split("/")
            vids.pop()
            self.streansNoRP = vids
            print("Pedido de quais videos exixtem no RP recebido")
        except Exception as e:
            print(f"Erro ao conectar ou enviar mensagens: {e}")

    def askStreamTransmission(self):
        self.clienteInterface()
        with self.condition:
            while self.streamSelected is None:
                self.condition.wait()

    def clienteInterface(self):
        self.janela = tk.Tk()
        self.janela.title("Servidor")
        print("Show interface1...")
        i = 0
        spacing = 10
        for stream in self.streansNoRP:
            #tela com nome
            self.label = tk.Label(self.janela, width=60, padx=spacing, pady=spacing)
            self.label["text"] = f"{stream}"
            self.label.grid(row=i, column=0, padx=spacing, pady=spacing)

            # Botao streamar e enviar a stream de video para o cliente		
            self.botaoStart = tk.Button(self.janela, width=30, padx=spacing, pady=spacing)
            self.botaoStart["text"] = "Select"
            self.botaoStart["command"] = lambda s=stream: self.selectStream(s)
            self.botaoStart.grid(row=i, column=1, padx=spacing, pady=spacing)
            i+=1
        self.janela.mainloop()

    def selectStream(self, video):
        print(f"{video} has been selected...")
        mensagem = f"Stream- {video}"
        self.server_socket.sendall((mensagem).encode())
        with self.condition:
            self.streamSelected = video
            self.condition.notify()
        self.janela.destroy()
    
    def waitselction(self):
        with self.condition:
            print("waiting")
            self.condition.wait()
    
    def streamTransmission(self):
        print("Cliente aguarda video...")
        # recebe o video em bytes do cliente
        while True:
            data = self.server_socket.recv(4096).decode('utf-8')

           



    '''
    def clienteInterface2(self): 
        print("Show interface...")
        i = 0
        for strean in self.streansNoRP:
            #tela com nome
            self.label = tk.Label(self.janela, width=20, padx=3, pady=3)
            self.label["text"] = f"{strean}"
            self.label.grid(row=i, column=0, padx=2, pady=2)
            # Butao streamar e enviar a stream de video para o cliente		
            self.botaoStart = tk.Button(self.janela, width=20, padx=3, pady=3)
            self.botaoStart["text"] = "Play"
            self.botaoStart["command"] = self.playStream
            self.botaoStart.grid(row=i, column=1, padx=2, pady=2)
            # Butao pausa de enviar a stream de video para o cliente				
            self.botaoPause = tk.Button(self.janela, width=20, padx=3, pady=3)
            self.botaoPause["text"] = "Pause"
            self.botaoPause["command"] = self.pauseStream
            self.botaoPause.grid(row=i, column=2, padx=2, pady=2)    
            # Para de streamar o video
            self.botaoClose = tk.Button(self.janela, width=20, padx=3, pady=3)
            self.botaoClose["text"] = "Close"
            self.botaoClose["command"] =  self.closeStream
            self.botaoClose.grid(row=i, column=3, padx=2, pady=2)
            i+=1

    def playStream(self, video):
        #pedir stream ao RP
        print("Pedido de envio do video "+video+ " ao servidor "+ self.socket_address)
        #receber os dados
        print("A receber video")
    
    def pauseStream(self):
        print("Stream Paused...")

    def closeStream(self):
        print("Stream close")
    '''

if __name__ == "__main__":
    try:
        filename = "config_file.txt"

        # Criar um cliente
        #janela = tk.Tk()
        #janela.geometry("800x600")  # Set the window size to 800x600 pixels
        cliente = ClienteGUI(filename)
        #cliente.janela.title("Servidor")
        #janela.mainloop()
    except Exception as e:
        print(f"Erro: {e}")
        print("[Usage: Cliente.py]\n")