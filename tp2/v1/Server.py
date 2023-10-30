import socket
import sys
from NodeData import *
from time import sleep
import threading

def interfaceServidor_1():
    print("########################################")
    print("#            Server Menu               #")
    print("########################################")
    print("# 1- Stream de mensagens               #")
    print("# 2- Stream de video da camara         #")
    print("# 3- Fechar Streams                    #")
    print("########################################")
    return input("Option: ")

def getPorta():
    print("########################################")
    print("#            Server Menu               #")
    print("########################################")
    print("#   Digite o numero de porta a usar    #")
    print("#                                      #")
    print("#                                      #")
    print("########################################")
    return input("PORTA: ")

def openServerOutput(ip, porta): 
    bindAddress = (ip, porta)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect(bindAddress)
    print("Servidor connectado ao RP!!!")
    # Servidor envia os dados que pretende ao RP
    i = 0
    while i < 50:
        response = f"Connection test-{i}"
        client_socket.send(response.encode())
        print(f"Servidor envou ao RP: {response}")
        i+=1
        sleep(1)
    # Fecha o socket do cliente
    client_socket.close()


def main(file):
    Node_Data = NodeData()
    Node_Data.parse_file(file)
    Node_Data.tostring()

    #database - associar a um conteudo a thread que esta a streamar esse conteudo 

    while True:
        opcao = interfaceServidor_1()
        porta = getPorta()
        if opcao == "1":
            thread = threading.Thread(target=openServerOutput, args=(Node_Data.RP_IP, int(porta)))
            thread.start()
        elif opcao == "2":
            #video stream 
            return 
        elif opcao == "3":
            #close threads 
            return 
        elif opcao == "0":
            #close server
            break


if __name__ == "__main__":
    if len(sys.argv) > 1:
        argumento = sys.argv[1]
        main(argumento)
    else:
        print("ERROR: Nenhum argumento passado à função Server.py!!")