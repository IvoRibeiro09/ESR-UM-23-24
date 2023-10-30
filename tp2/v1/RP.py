import sys
import threading
import socket
from NodeData import *
from time import sleep
import queue

#global_data = []
#lock = threading.Lock()  # Um lock para garantir acesso seguro às variáveis globais

def connectionAcception(q, event, client_socket, client_address):
    while True:
        resposta = client_socket.recv(1024).decode()
        if not resposta:
            # If the received message is empty, it means the client closed the connection
            print(f"Connection closed by {client_address}")
            break
        #global_data.append(resposta)
        q.put(resposta)
        event.set()
        print(f"Received:\"{resposta}\" from IP:{client_address}")
      
    client_socket.close()


def openServerSocket(q, event, serverIp, porta):
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
            thread0 = threading.Thread(target=connectionAcception, args=(q,event, client_socket,client_address))
            thread0.start()

        except Exception as e:
            server_socket.close()
            print(f"Erro: {str(e)}")
            return 


def client_handler(q, event, client_socket):
    while not q.empty():
        message = q.get()
        #print("Mensagem enviada ao cliente: ", message)
    while True:
        # Define a mensagem a ser enviada aos clientes
        event.wait()
        message = q.get()  # Obtém a mensagem da fila
        event.clear()  # Limpa o sinal
        client_socket.send(message.encode())
        print("Mensagem enviada ao cliente: ", message)
        try:
            resposta = client_socket.recv(1024)
            if resposta.decode() == "Confirmado":
                print("Cliente confirmou o recebimento.")
        except ConnectionResetError:
            # Cliente desconectado
            break
    client_socket.close()


def openClientSocket(q, event, host, porta):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, porta))

    # esperar conexão
    server_socket.listen(1)
    print(f"Nodo {host} aguadar conexões na porta:{porta}")
    while True:
        try:
            # Aceita a conexão do cliente
            client_socket, client_address = server_socket.accept()
            # Inicia uma thread para lidar com o cliente
            thread0 = threading.Thread(target=client_handler, args=(q, event, client_socket,))
            thread0.start()

        except Exception as e:
            server_socket.close()
            print(f"Erro: {str(e)}")
            return 


def main(file):
    Node_Data = NodeData()
    Node_Data.parse_file(file)
    Node_Data.tostring()

    # Abrir uma porta de escuta
    portaDeEscuta = int(Node_Data.portaEscuta)
    ipDeEscutaDeServer = Node_Data.ip

    message_event = queue.Queue()
    event = threading.Event()
    
    thread = threading.Thread(target=openServerSocket, args=(message_event, event, ipDeEscutaDeServer, portaDeEscuta))
    thread.start()

    for neigh in Node_Data.neighboursNodes:
        thread = threading.Thread(target=openClientSocket, args=(message_event, event, neigh, portaDeEscuta))
        thread.start()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        argumento = sys.argv[1]
        main(argumento)
    else:
        print("ERROR: Nenhum argumento passado à função Node.py!!")