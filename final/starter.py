from time import sleep
from NodeGUI import NodeGUI
from NodeData import NodeData
from RPGUI import RPGUI
from ClienteGUI import ClienteGUI
from ServerGUI import ServerGUI

if __name__ == "__main__":
    try:
        # Obtém o endereço IP local da máquina
        ip = input("IP da maquina atual: ")
        filename = "config_file.txt"

        nodedata = NodeData(ip, filename)
        nodedata.tostring()

        if nodedata.getType() == "RendezvousPoint":
            rp = RPGUI(nodedata)
        else:
            node = NodeGUI(nodedata)
            if nodedata.getType() == "Client":
                sleep(5)
                cliente = ClienteGUI(nodedata)
            elif nodedata.getType() == "Server":
                sleep(3)
                servidor = ServerGUI(nodedata)

    except Exception as e:
        print(f'Ocorreu um erro: {str(e)}')