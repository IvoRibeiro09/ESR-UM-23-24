import socket
import sys
from NodeData import *
from time import sleep

def main(file):
    Node_Data = NodeData()
    Node_Data.parse_file(file)
    Node_Data.tostring()

    server_ip = "127.0.0.4"
    server_port = 12346

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    while True:
        mensagem = client_socket.recv(1024).decode()
        print(f"Recebido do servidor: {mensagem}")

        # Confirma o recebimento
        confirmacao = "Confirmado"
        client_socket.send(confirmacao.encode())


if __name__ == "__main__":
    if len(sys.argv) > 1:
        argumento = sys.argv[1]
        main(argumento)
    else:
        print("ERROR: Nenhum argumento passado à função Cliente.py!!")