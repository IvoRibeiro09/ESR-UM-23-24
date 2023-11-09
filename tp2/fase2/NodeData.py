class NodeData:
    def __init__(self):
        self.ip = ""
        self.porta = ""
        self.type = ""
        self.rp_ip = ""
        self.nosadjacentes = []

    # Getters
    def getip(self):
        return str(self.ip)

    def getporta(self):
        return str(self.porta)

    def gettype(self):
        return str(self.type)

    def getrp_ip(self):
        return str(self.rp_ip)

    def getnosajd(self):
        return str(self.nosadjacentes)

    # Setters
    def setip(self, ip):
        self.ip = ip

    def setporta(self, porta):
        self.porta = porta

    def setype(self, type):
        self.type = type

    def setrp_ip(self, rp_ip):
        self.rp_ip = rp_ip

    def setnosajd(self, adjacentes):
        self.nosadjacentes = adjacentes

    def addNode(self, node):
        self.nosadjacentes.append(node)

    def parse_file(self, filepath):
        file = open(filepath)
        counter = 0
        for i in file:
            counter += 1
            if counter == 1:
                ip_porta = i.strip("\n").split()
                self.setip(ip_porta[0])
                self.setporta(ip_porta[1])
            elif counter == 2:
                self.setype(i.strip("\n"))
            elif counter == 3:
                self.setrp_ip(i.strip("\n"))
            else:
                self.addNode(i.strip("\n"))

    def tostring(self):
        print("-----------------------------------------------")
        print("IP: " + self.ip)
        print("Porta: "+ self.porta)
        print("Type: " + self.type)
        print("RP IP: " + self.rp_ip)
        for i in self.nosadjacentes:
            print("Nó Adjacente: " + i)
        print("-----------------------------------------------")
