import os.path

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

def ClienteMenu():
    option = interfaceCliente_1()
    if option == 1:
        #pedido ao RP daquilo que ele tem la
        #receber a info do RP

        #display das opcoes

        #pedido ao RP daquilo que ele quer ver
        #começar a transmissao
    else:
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

def ServidorMenu():
    file = interfaceServidor_1()
    while not valida_ficheiro(file):
        file = interfaceServidor_1()
    #transmitir o conteudo em unicast para o RP



def main():

    NodeData = parse(file)

    # iniciar duas threads uma para gerir a funçao de No de cada no
    # e outra para se ele for um tipo de alguma coisa fazer o que é suposto fazer
    # esta ultima thread pode morrer se ele nao tiver tipo para nao estar sempre sem fazer nada

    #cliente
    if NodeData.type == 1:
        ClienteMenu()

    #servidor
    elif NodeData.type == 2:
        ServidorMenu()

    #RP
    elif NodeData.type == 3:
        #fazer flush
        #registar todos os caminhos
        #ficar à espera de comunicaçao cliente ou Servidor
