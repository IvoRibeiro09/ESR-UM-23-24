import os.path
import socket
import threading
import sys
from time import sleep

from NodeData import *


# começa a correr quando a outra da start
# primeiro da parse do ficheiro para saber o ip e o seu tipo
# depois consuante o seu tipo faz alguma cena
# se for cliente tem um menu onde ele pode perguntar ao servidor RP o que ele pode aceder
# se for servidor tem um menu onde pode dizer o que quer streamar
# se for RP tem de ser capaz de fazer flush e reconhecer os caminhos de menor custo na rede Overlay
def interfaceCliente_1():
    print("########################################")
    print("#            Client Menu               #")
    print("########################################")
    print("#   1- Saber o que esta na rede        #")
    print("#                                      #")
    print("#                                      #")
    print("########################################")
    return input("Option: ")


def clienteMenu():
    option = interfaceCliente_1()
    if option == 1:
        return
        #pedido ao RP daquilo que ele tem la
        #receber a info do RP

        #display das opcoes

        #pedido ao RP daquilo que ele quer ver
        #começar a transmissao
    else:
        return
        #nao sei se tem de fazer mais alguma coisa para alem disto
        #por exemplo pode desligar e este nodo fico apenas como nodo
        # na rede overlay e deixa de ser nodo e cliente


def interfaceServidor_1():
    print("########################################")
    print("#            Server Menu               #")
    print("########################################")
    print("#   Digite o ficheiro e respetivo      #")
    print("#   caminho que deseja transmitir      #")
    print("#   na rede                            #")
    print("########################################")
    return input("Option: ")


def valida_ficheiro(file):
    return os.path.isfile(file)


def servidorMenu():
    file = interfaceServidor_1()
    while not valida_ficheiro(file):
        file = interfaceServidor_1()
    #transmitir o conteudo em unicast para o RP
    #verificar que o Rp recebeu


def FuncaoType(NodeData):
    # cliente
    if NodeData.type == 1:
        clienteMenu()

    #servidor
    elif NodeData.type == 2:
        servidorMenu()

    #RP
    elif NodeData.type == 3:
        return
        #fazer flush
        #registar todos os caminhos por ordem de menor salto
        #ficar à espera de comunicaçao cliente ou Servidor


def linktest(ipDest, porta):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the destination IP and port
        client_socket.connect((ipDest, porta))

        # recebe a mesnsagem de conexao
        message = client_socket.recv(1024)
        print(f"Recebido do {ipDest}: {message.decode()}")

        # resopnde afirmativamente
        response = "Received and acknowledged!"
        client_socket.send(response.encode())

        client_socket.close()
        return True
    except Exception as e:
        #print(f"Erro: {str(e)}")
        return False


def ConnectionTest(NodeData):
    for nodeAndPort in NodeData.nosadjacentes:
        values = nodeAndPort.split()
        resposta = linktest(values[0], int(values[1]))
        print(f"Connection test recebida do IP:{values[0]} com Resposta: {resposta}")
        if not resposta:
            return False
    return True


def ReciveTestMsg(host_ip, porta):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host_ip, porta))
    # esperar conexoes
    server_socket.listen(1)
    print(f"Nodo {host_ip} aguadar conexões na porta:{porta}")
    # aceita a conexao
    while True:
        try:
            # Configura um timeout de 10 segundos
            server_socket.settimeout(10)

            # Aceita a conexão do cliente
            client_socket, client_address = server_socket.accept()
            print(f"Enviei teste de conexão ao IP: {client_address}")
            mensagem = "Connection test"
            client_socket.send(mensagem.encode())

            # Aguarda a resposta ao teste
            resposta = client_socket.recv(1024).decode()
            print(f"recebi resposta: {resposta} do Ip: {client_address}")
            client_socket.close()
        except socket.timeout:
            server_socket.close()
            print("Timeout: Nenhum cliente conectou em 10 segundos.")


def main(file):
    Node_Data = NodeData()
    Node_Data.parse_file(file)
    Node_Data.tostring()


    #teste de conectividade
    thread0 = threading.Thread(target=ReciveTestMsg, args=(Node_Data.ip, int(Node_Data.porta)))
    thread0.start()
    # flush inicial para garantir conectividade com os nos adjacentes tcp
    # recebe uma mensagem a dizer que esta conectado

    if not ConnectionTest(Node_Data):
        return f"Erro: IP-{str(Node_Data.ip)} erro ao connectar aos seus vizinhos"

    # iniciar duas threads uma para gerir a funçao de No de cada no
    # e outra para se ele for um tipo de alguma coisa fazer o que é suposto fazer
    # esta ultima thread pode morrer se ele nao tiver tipo para nao estar sempre sem fazer nada
    print("Finalizei a conexão de teste!")
    # uma Thread
    if Node_Data.type != 0:
        threading.Thread(target=FuncaoType, args=Node_Data)

    # uma Thread

    # espera receber uma mensagem com o destino e o conteudo que tem de enviar
    #TCP

    # envia o conteudo para esse destino
    # guard a info do que esta a partilhar


if __name__ == "__main__":
    if len(sys.argv) > 1:
        argumento = sys.argv[1]
        main(argumento)
    else:
        print("ERROR: Nenhum argumento passado à função NodeOverlay.py!!")