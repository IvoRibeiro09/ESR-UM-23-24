import socket
import sys
from NodeData import *

def main(file):
    Node_Data = NodeData()
    NodeData.parse_file(file)
    NodeData.tostring()

    # Abrir uma porta de escuta
    porta = 3000
    host = "127.0.0.1"
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(host, porta)

    # esperar conexão
    server_socket.listen(1)
    print(f"Nodo {host} aguadar conexões na porta:{porta}")
    while True:
        try:
            # Aceita a conexão do cliente
            client_socket, client_address = server_socket.accept()
            print(f"Enviei teste de conexão ao IP: {client_address}")
            mensagem = "Connection test"
            client_socket.send(mensagem.encode())

            # Aguarda a resposta ao teste
            resposta = client_socket.recv(1024).decode()
            print(f"recebi resposta: {resposta} do Ip: {client_address}")
            client_socket.close()
        except Exception as e:
            server_socket.close()
            print(f"Erro: {str(e)}")
            return 



if __name__ == "__main__":
    if len(sys.argv) > 1:
        argumento = sys.argv[1]
        main(argumento)
    else:
        print("ERROR: Nenhum argumento passado à função NodeOverlay.py!!")