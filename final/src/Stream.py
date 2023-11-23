import socket
from src.auxiliarFunc import *
from src.Packet import *
from src.NodeData import *

'''
Esta é a classe Stream implementada para auxiliar o RP a gerenciar as Streams no que toca 
a receber e enviar dados, e gerenciar para quem continuar a mandar assim como o caminho 
por onde a informação tem de passar
'''
class Stream():
    def __init__(self, name, nodePort, server):
        self.name = name
        self.nodePort = nodePort
        self.server_address = server
        self.status = "Closed" # "Pending" "Streaming"
        self.stream_track = None
        self.Node_Track = []
           
    # getters
    def getName(self):
        return str(self.name)
    
    def getStatus(self):
        return str(self.status)
    
    def getServerAddress(self):
        return self.server_address
    
    def getNodeTrack(self):
        return self.Node_Track

    # Metodo que adiciona um cliente a uma stream o que significa que o rp tera de enviar 
    # os dados que recebe do servidor desta stream segundo o caminho que definiu como 
    # sendo o melhor 
    def addClient(self, ip_cliente, caminhosdoRP):
        print(f"Client {ip_cliente} connectado à Stream {self.name}")
        # Tratar do caso em que é o primeiro cliente a pedir a Stream
        if self.status == "Closed":
            try:
                self.status = "Pending"
                # escolher o caminho mais rapido
                for cam in caminhosdoRP:
                    if ip_cliente in cam:
                        self.stream_track = cam
                # defenir qual o neighbour por onde enviar
                extrair_conexoes(self.Node_Track, self.stream_track)
                
                # Notificar o servidor que pode enviar esta stream que pode começar a enviar
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                    try:
                        server_socket.connect(self.server_address)
                
                        msg = f"Start Stream- {self.name}"
                        data = msg.encode('utf-8')
                        server_socket.send(data)
                    except Exception as e:
                        print(f"Erro ao enviar o pedido de stream ao servidor: {e}")
                    finally:
                        server_socket.close()   
                self.status = "Streaming"
            except Exception as e:
                print(f"Erro na adição do primeiro cliente à stream: {e}")
        # Tratar do caso em que ja esta a ser stream ja esta a ser enviada para um outro cliente
        elif self.status == "Streaming":
            try:
                # escolher o caminho mais rapido para o cliente em questao
                caminho = ""
                for cam in caminhosdoRP:
                    if ip_cliente in cam:
                        caminho = cam
                # verificar se o caminho ideal para o segundo cliente tem alguma conexão em comum com a atual
                possibel = possibelToMerge(caminho, self.stream_track)
                
                # Caso tenho alguma em comum vamos combinar os caminhos e fazer apenas um 
                if possibel == True:
                    self.stream_track = combinar_caminhos(self.stream_track, caminho)
                    self.Node_Track = []
                    extrair_conexoes(self.Node_Track, self.stream_track)
                # Caso nao seja possivel combinar apenas adicionamos o segundo caminho 
                else:
                    extrair_conexoes(self.Node_Track, caminho)
            except Exception as e:
                print(f"Erro na adição do cliente a stream ja aberta: {e}")

    # Metodo que envia a Stream para os vizinhos necessarios reestroturando o pacote com os dados
    # relativos as conexões e direções para onde o pacote tem de ser enviado
    def sendStream(self, frameNumber, frame):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as stream_socket:
                try:
                    for track in self.Node_Track:
                        # Criar o pacote com o caminho ate os cliente
                        pck = Packet(track[1], frameNumber, frame)
                        dataToSend = pck.buildPacket()
                        send_address = (track[0], self.nodePort)
                        
                        stream_socket.sendto(dataToSend, send_address)
                except Exception as e:
                    print(f"Error sending stream from RP: {e}")
        except Exception as e:
            print(f"Error creating and sending the packet from RP: {e}")

    # Metodo que remove um cliente de assistir à Stream reformulando os caminhos 
    # verificando se o servidro ainda precisa de enviar a Stream
    def rmvClient(self, client_ip):
        try:
            for track in self.Node_Track:
                if client_ip in track[1]:
                    new_track = splitTracks(track[1], client_ip)
                    if new_track:
                        self.Node_Track.append((track[0], new_track))
                    self.Node_Track.remove(track)
                    if self.Node_Track == []:
                        self.status = "Closed"
                    break
        
        except Exception as e:
            print("Erro ao remover o caminho para o cliente que deu dsiconnect: ", e)