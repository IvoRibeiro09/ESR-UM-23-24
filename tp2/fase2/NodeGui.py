
class NodeGUI:
    def __init__(self, ip):
        self.IP = None
        self.portaEscuta = None
        self.adjacentes = []
        self.start()

    def start(self):
        #uma thread a receber conexoes
        #quando recebe verifica se o seu nome nao esta presente 
        # se estiver nao faz nada
        # se nao estiver mete o seu ip na mesnagem e envia aos seus visinhos
        pass
    
    def connectionTest(self, mensagem):
        for adj in self.adjacentes:
            if not (mensagem['nome'] == adj[0] and mensagem['ip'] == adj[1]):
                pass

    # ter uma janela que ao ligar tem as opçoes testar conexao e espera o clique para cemçar a testar