import socket

class Stream():

    def __init__(self, name, server, caminhos):
        self.name = name
        self.server_address = server
        self.status = "Closed" # "Pending" "Streaming"
        self.caminhosdoRP = caminhos
        self.caminhoDaStream = ""
        self.clientList = []
        # 127.0.0.5 <- 127.0.0.4 <- 127.0.0.3
        # 127.0.0.5 <- 127.0.0.4 | 127.0.0.4 <- 127.0.0.3

        # 127.0.0.5 <- 127.0.0.4 <- 127.0.0.3 and 127.0.0.6 <- 127.0.0.4 <- 127.0.0.3
        # 127.0.0.5 <- 127.0.0.4 | 127.0.0.6 <- 127.0.0.4 | 127.0.0.4 <- 127.0.0.3
             
    # getters
    def getName(self):
        return str(self.name)
    
    def getStatus(self):
        return str(self.status)
    
    # setters
    
    def addClient(self, ip_cliente):
        ip_cliente = '127.0.0.5'
        print(f"Client {ip_cliente} connectado à Stream {self.name}")
        if self.status == "Closed":
            self.status = "Pending"
            # e cria o caminho ideal para enviar a stream
            self.caminhoDaStream = "127.0.0.3 -> 127.0.0.4 | 127.0.0.4 -> 127.0.0.5"
            
            # notify server to start stream tpc 
            server_address = (self.server_address)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                try:
                    server_socket.connect(server_address)
            
                    msg = f"Stream- {self.name}"
                    data = msg.encode('utf-8')
                    server_socket.send(data)
                except Exception as e:
                    print(f"Erro ao conectar ou enviar mensagens de stream ao servidor: {e}")
                finally:
                    server_socket.close()   
            self.status = "Streaming"
        elif self.status == "Streaming":
            pass
        # verificar se o caminho pode ser commun e se poder alterar o caminho de envio

    def sendStream(self, pacote):
        for cli in self.clientList:
            if self.status == "Streaming":
                pass
            # verificar se os camimhos por onde passam a stream ja enviada coincidem
            # com algum caminho do spossiveis para o ip
            else:
                pass
            # enviar pelo caminho mais curto e guardar os nos por onde o pacote passa
            self.status = "Streaming"

    