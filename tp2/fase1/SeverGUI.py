import socket
from auxiliarFunc import *

class ServerGUI:

    def __init__(self, file):
        #self.IP = getIP
        self.IP = '127.0.0.2'
        self.ipDoRP = None
        self.portaDoRP = None
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.videoList = []
        self.parse(file)
        self.serverStarter()

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
                    elif "ip_rp- " in line:
                        self.ipDoRP = extrair_conteudo(line)
                    elif "porta_rp- " in line:
                        self.portaDoRP = extrair_numero_porta(line)
                    elif "stream- " in line:
                        self.videoList.append(extrair_conteudo(line))

    def serverStarter(self):
        print("Starter...")
        self.conectToRP()
    
    def conectToRP(self):
        try:
            server_address = (self.ipDoRP, self.portaDoRP)
            self.server_socket.connect(server_address)
            print("Servidor conectado ao RP")

            # enviar os videos que você tem para exibir
            for video in self.videoList:
                msg = f"ADD-{video[0]}".encode('utf-8')
                self.server_socket.sendall(msg)

            # enviar mensagem de que já enviou tudo
            end_msg = "-END".encode('utf-8')
            self.server_socket.sendall(end_msg)

            print("RP informado dos vídeos que o servidor tem disponíveis...")
        except Exception as e:
            print(f"Erro ao conectar ou enviar mensagens: {e}")


if __name__ == "__main__":
    try:
        filename = "config_file.txt"

        # Criar um Servidor
        rp = ServerGUI(filename)
    except:
        print("[Usage: Server.py]\n")	