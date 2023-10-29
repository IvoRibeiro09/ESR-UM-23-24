class NodeData:
    def __init__(self):
        self.type = None
        self.ip = None
        self.portaEscuta = None
        self.RP_IP = None
        self.RP_PORTA = None
        self.neighboursNodes = []

    # Getters
    def gettype(self):
        return str(self.type)
    
    def getip(self):
        return str(self.ip)

    def getportaEscuta(self):
        return str(self.portaEscuta)

    def getrp_ip(self):
        return str(self.RP_IP)
    
    def getrp_porta(self):
        return str(self.RP_PORTA)

    def getneighbours(self):
        return str(self.neighboursNodes)

    # Setters
    def settype(self, type):
        self.type = type

    def setip(self, ip):
        self.ip = ip

    def setportaEscuta(self, porta):
        self.portaEscuta = porta

    def setrp_ip(self, rp_ip):
        self.RP_IP = rp_ip

    def setrp_porta(self, rp_porta):
        self.RP_PORTA = rp_porta

    def setneighbours(self, neigh):
        self.neighboursNodes.append(neigh)

    # parser    
    def parse_file(self, filepath):
        file = open(filepath)
        lines = file.readlines()

        # Process each line and extract the host_ip value
        for index, line in enumerate(lines):
            if '---TYPE---' in line:
                if index + 1 < len(lines):
                    self.settype(lines[index + 1].strip())
            elif '---HOST_IP---' in line:
                if index + 1 < len(lines):
                    self.setip(lines[index + 1].strip())
            elif '---PORTA_DE_ESCUTA---' in line:
                if index + 1 < len(lines):
                    self.setportaEscuta(lines[index + 1].strip())
            elif '---RP_IP---' in line:
                if index + 1 < len(lines):
                    self.setrp_ip(lines[index + 1].strip())
            elif '---RP_PORTA---' in line:
                if index + 1 < len(lines):
                    self.setrp_porta(lines[index + 1].strip())
            elif '---NEIGHBOURS_NODES---' in line:
                while index + 1 < len(lines):
                    self.setneighbours(lines[index + 1].strip())
                    index += 1

    # print
    def tostring(self):
        print("-----------------------------------------------")
        print("Type: " + str(self.type))
        print("IP: " + str(self.ip))
        if self.portaEscuta:
            print("Porta Escuta: " + str(self.portaEscuta))
        if self.RP_IP:
            print("RP IP: " + str(self.RP_IP))
        if self.RP_PORTA:
            print("RP Porta: " + str(self.RP_PORTA))
        for i in self.neighboursNodes:
            print("Nó Adjacente: " + str(i))
        print("-----------------------------------------------")