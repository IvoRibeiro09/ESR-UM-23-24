import socket
import sys
import threading
from time import sleep
from NodeData import *


def openServerSocket(serverIp, porta):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((serverIp, porta))

    # esperar conexão
    server_socket.listen(1)
    print(f"Nodo {serverIp} aguadar conexões na porta:{porta}")
    while True:
        try:
            # Aceita a conexão do cliente
            client_socket, client_address = server_socket.accept()
            # dedica uma thread a esse cliente
            thread0 = threading.Thread(target=connectionAcception, args=(client_socket,client_address))
            thread0.start()

        except Exception as e:
            server_socket.close()
            print(f"Erro: {str(e)}")
            return 


def connectionAcception(client_socket, client_address):
    i = 0
    print(f"Enviei teste de conexão ao IP: {client_address}")

    while i < 5 :
        mensagem = "Connection test"
        client_socket.send(mensagem.encode())

        # Aguarda a resposta ao teste
        resposta = client_socket.recv(1024).decode()
        print(f"recebi resposta: {resposta} do Ip: {client_address}")
        i+=1
        sleep(10)

    client_socket.close()

def main(file):
    Node_Data = NodeData()
    Node_Data.parse_file(file)
    Node_Data.tostring()

    # Abrir uma porta de escuta
    portas = [3000,4000]
    host = "127.0.0.2"
    
    for porta in portas:
        thread = threading.Thread(target=openServerSocket, args=(host, porta))
        thread.start()
  


if __name__ == "__main__":
    if len(sys.argv) > 1:
        argumento = sys.argv[1]
        main(argumento)
    else:
        print("ERROR: Nenhum argumento passado à função NodeOverlay.py!!")