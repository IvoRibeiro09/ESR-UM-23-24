import threading
import socket
from auxiliarFunc import *
import tkinter as tk

class NodeGUI:
    def __init__(self, ip, file):
        self.janela = None
        self.IP = ip
        self.portaEscuta = None
        self.adjacentes = []
        self.parse(file)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nodeState = True
        self.condition = threading.Condition()
        self.conditionBool = False
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
        # ter uma janela que ao ligar tem as opçoes testar conexao e espera o clique para cemçar a testar
        # iniciar a thread que receve conexoes que so ira ser fechada quando clicar em close
        # iniciar o connection test qunado clicar no botao start teste connection
        thread0 = threading.Thread(target=self.recieveConnection)
        thread1 = threading.Thread(target=self.connectionTest)
        thread0.start()
        thread1.start()
    
    def connectionTest(self):
        self.janela = tk.Tk()
        self.janela.title(f'Node: {self.IP}')
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

        msg = self.IP
        self.sendMessageToAdjacentNodes(msg)

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
        socket_address = (self.IP, self.portaEscuta)
        self.server_socket.bind(socket_address)
        self.server_socket.listen()
        while self.nodeState:
            try:
                client_connection, client_address = self.server_socket.accept()
                print(f"Node {client_address[0]} send connection test to: {self.IP}")

                size = client_connection.recv(4)
                msg_size = int.from_bytes(size, byteorder='big')
                        
                msg = b""
                while len(msg) < msg_size:
                    msg += client_connection.recv(msg_size - len(msg))
                        
                mensagem = msg.decode('utf-8')

                if self.IP not in mensagem:
                    mensagem = mensagem + " -> " + self.IP
                    self.sendMessageToAdjacentNodes(mensagem)

            except Exception as e:
                print(f"Erro na receção de conexões no Nodo {self.IP}")
                
    def sendMessageToAdjacentNodes(self, mensagem):
        for adj in self.adjacentes: 
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((adj[0], adj[1]))

                    msg = (
                        len(mensagem).to_bytes(4, 'big') +
                        mensagem.encode('utf-8')
                    )
                    s.sendall(msg)
                
            except Exception as e:
                print(f"Não foi possível enviar mensagem para {adj[1]}:{adj[2]}. Erro: {str(e)}")
            finally:
                # Certifique-se de que a conexão seja fechada mesmo em caso de exceção
                s.close()



if __name__ == "__main__":
    try:
        # Obtém o endereço IP local da máquina
        ip = input("IP da maquina atual:")
        filename = "config_file.txt"
        print(ip)
        node = NodeGUI(ip, filename)
        #node.janela.mainloop()

    except Exception as e:
        print(f'Ocorreu um erro: {str(e)}')