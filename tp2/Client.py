import socket
import sys
from NodeData import *

def main(file):
    Node_Data = NodeData()
    Node_Data.parse_file(file)
    Node_Data.tostring()

    server_host = "127.0.0.1"
    porta = 3000

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((server_host, porta))
    
    message = client_socket.recv(1024)
    message = client_socket.recv(1024)
    print(f"Recebido do servidor: {message.decode()}")

    # Responde com uma mensagem afirmativa
    response = "Conectividade confirmada"
    client_socket.send(response.encode())

    # Fecha o socket do cliente
    client_socket.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        argumento = sys.argv[1]
        main(argumento)
    else:
        print("ERROR: Nenhum argumento passado à função NodeOverlay.py!!")