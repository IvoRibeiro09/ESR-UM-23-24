
class Stream():

    def __init__(self, name, server, caminhos):
        self.name = name
        self.server_address = server
        #self.clientList = []
        self.status = "Closed" # "Pending" "Streaming"
        self.caminhosdoRP = caminhos
        self.caminhoDaStream = []
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
    
    def addClient(self, c):
        if self.status == "Closed":
            self.status = "Pending"
            # notify server to start stream tpc
            # abre a socket udp para receber os pacotes de video 
            # e cria o caminho ideal para enviar a stream

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

    