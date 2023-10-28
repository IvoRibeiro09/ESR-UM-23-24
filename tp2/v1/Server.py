import socket
import sys
from NodeData import *
from time import sleep

def main(file):
    Node_Data = NodeData()
    Node_Data.parse_file(file)
    Node_Data.tostring()

    RP_host = "127.0.0.1"
    porta = 12345

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((RP_host, porta))
    print("Servidor connectado ao RP!!!")
    # Servidor envia os dados que pretende ao RP
    i = 0
    while i < 25:
        response = "Connection test"
        client_socket.send(response.encode())
        print(f"Servidor envou ao RP: {response}")
        i+=1
        sleep(6)
    # Fecha o socket do cliente
    client_socket.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        argumento = sys.argv[1]
        main(argumento)
    else:
        print("ERROR: Nenhum argumento passado à função Server.py!!")