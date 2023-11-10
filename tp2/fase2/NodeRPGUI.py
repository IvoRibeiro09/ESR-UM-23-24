import socket


class NodeRpGUI:
    def __init__(self, name):
        self.janela = None
        self.IP = ip
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

if __name__ == "__main__":
    try:
        # Obtém o endereço IP local da máquina
        ip = input("IP da maquina atual:")
        filename = "config_file.txt"
        print(ip)
        noderp = NodeRPGUI(ip, filename)
        #cliente.janela.mainloop()

    except Exception as e:
        print(f'Ocorreu um erro: {str(e)}')