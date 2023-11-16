import socket
from auxiliarFunc import *
from Packet import *

class Stream():
    def __init__(self, name, server):
        self.name = name
        self.server_address = server
        self.status = "Closed" # "Pending" "Streaming"
        self.Node_Track = []
           
    # getters
    def getName(self):
        return str(self.name)
    
    def getStatus(self):
        return str(self.status)
    

    
    def addClient(self, ip_cliente, caminhosdoRP):
        print(f"Client {ip_cliente} connectado à Stream {self.name}")
        if self.status == "Closed":
            try:
                self.status = "Pending"
                # escolher o caminho mais rapido
                caminho = ""
                for cam in caminhosdoRP:
                    if ip_cliente in cam:
                        caminho = cam
                # defenir qual o neighbour por onde enviar
                extrair_conexoes(self.Node_Track, caminho)
                
                # notify server to start stream tpc 
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                    try:
                        server_socket.connect(self.server_address)
                
                        msg = f"Stream- {self.name}"
                        data = msg.encode('utf-8')
                        server_socket.send(data)
                    except Exception as e:
                        print(f"Erro ao enviar o pedido de stream ao servidor: {e}")
                    finally:
                        server_socket.close()   
                self.status = "Streaming"
            except Exception as e:
                print(f"Erro na adição do primeiro cliente à stream: {e}")
        elif self.status == "Streaming":
            try:
                print("A stream já está a ser transmitida")
                # escolher o caminho mais rapido para o cliente em questao
                caminho = ""
                for cam in caminhosdoRP:
                    if ip_cliente in cam:
                        caminho = cam
                # verificar se o caminho pode ser commun e se poder alterar o caminho de envio
                print("lista node track antes do merge", self.Node_Track)
                track_to_change = possibelToMerge(caminho, self.Node_Track)
                if track_to_change:
                    new_track = mergeCaminhos(caminho, track_to_change)
                    self.Node_Track.append(new_track)
                else:
                    extrair_conexoes(self.Node_Track, caminho)
                print("lista node track depois do merge", self.Node_Track)
            except Exception as e:
                print(f"Erro na adição do cliente a stream ja aberta: {e}")

    def sendStream(self, pacote):
        try:
            #e enviar para todos os clientes
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as stream_socket:
                try:
                    for nei in self.Node_Track:
                        #fazer o pacote trackeado
                        pck = TrackedPacket(nei[1], pacote)
                        dataToSend = pck.buildTrackedPacket()
                        send_address = (nei[0], Node_Port)
                        #print("RP send to: ", send_address)
                        stream_socket.sendto(dataToSend, send_address)
                except Exception as e:
                    print(f"Error sending stream from RP: {e}")
        except Exception as e:
            print(f"Error creating and sending the packet from RP: {e}")