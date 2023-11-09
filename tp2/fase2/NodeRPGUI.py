
class NodeRp:
    def __init__(self, name):
        self.ip = "127.0.0.1"
        self.portaEscuta = 12345
        self.adjacentes = []
        self.caminhos = []
        self.start()

    def start(self):
        # abrir a socket que espera receber mensagens com os caminhos
        # guardar os caminhos
        pass

    def printCaminhos(self):
        for caminho in self.caminhos:
            print(caminho)