import sys
import threading
import socket
from NodeData import *
from time import sleep

global_data = []
#lock = threading.Lock()  # Um lock para garantir acesso seguro às variáveis globais


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
    while True:
        resposta = client_socket.recv(1024).decode()
        if not resposta:
            # If the received message is empty, it means the client closed the connection
            print(f"Connection closed by {client_address}")
            break
        global_data.append(resposta)
        print(f"Received:\"{resposta}\" from IP:{client_address}")
      
    client_socket.close()


def client_handler(client_socket):
    while True:
        # Define a mensagem a ser enviada aos clientes
    #    with lock:
        data = global_data.pop()
        print("data--" + data)
        client_socket.send(data.encode())

        try:
            resposta = client_socket.recv(1024)
            if resposta.decode() == "Confirmado":
                print("Cliente confirmou o recebimento.")
        except ConnectionResetError:
            # Cliente desconectado
            break

        sleep(6)

    client_socket.close()

def openClientSocket(host, porta):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, porta))

    # esperar conexão
    server_socket.listen(1)
    print(f"Nodo {host} aguadar conexões na porta:{porta}")


    client_socket, client_address = server_socket.accept()
    # Inicia uma thread para lidar com o cliente
    thread0 = threading.Thread(target=client_handler, args=(client_socket,))
    thread0.start()


def main(file):
    Node_Data = NodeData()
    Node_Data.parse_file(file)
    Node_Data.tostring()

    # Abrir uma porta de escuta
    portaDeEscuta = Node_Data.portaEscuta
    ipDeEscutaDeServer = Node_Data.ip
    
    thread = threading.Thread(target=openServerSocket, args=(ipDeEscutaDeServer, portaDeEscuta))
    thread.start()

    # porta = 12346
    # host = "127.0.0.4"
    for neigh in Node_Data.neighboursNodes:
        thread = threading.Thread(target=openClientSocket, args=(neigh, portaDeEscuta))
        thread.start()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        argumento = sys.argv[1]
        main(argumento)
    else:
        print("ERROR: Nenhum argumento passado à função Node.py!!")