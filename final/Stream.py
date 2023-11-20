import socket
from auxiliarFunc import *
from Packet import *

class Stream():
    def __init__(self, name, server):
        self.name = name
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

    def addClient(self, ip_cliente, caminhosdoRP):
        print(f"Client {ip_cliente} connectado à Stream {self.name}")
        if self.status == "Closed":
            try:
                self.status = "Pending"
                # escolher o caminho mais rapido
                for cam in caminhosdoRP:
                    if ip_cliente in cam:
                        self.stream_track = cam
                # defenir qual o neighbour por onde enviar
                extrair_conexoes(self.Node_Track, self.stream_track)
                
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
                # escolher o caminho mais rapido para o cliente em questao
                caminho = ""
                for cam in caminhosdoRP:
                    if ip_cliente in cam:
                        caminho = cam
                # verificar se o caminho pode ser commun e se poder alterar o caminho de envio
                possibel = possibelToMerge(caminho, self.stream_track)
                if possibel == True:
                    self.stream_track = combinar_caminhos(self.stream_track, caminho)
                    self.Node_Track = []
                    extrair_conexoes(self.Node_Track, self.stream_track)
                else:
                    extrair_conexoes(self.Node_Track, caminho)
            except Exception as e:
                print(f"Erro na adição do cliente a stream ja aberta: {e}")

    def sendStream(self, frameNumber, frame):
        try:
            #e enviar para todos os clientes
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as stream_socket:
                try:
                    for nei in self.Node_Track:
                        #fazer o pacote trackeado
                        pck = Packet(nei[1], frameNumber, frame)
                        dataToSend = pck.buildPacket()
                        send_address = (nei[0], Node_Port)
                        
                        stream_socket.sendto(dataToSend, send_address)
                except Exception as e:
                    print(f"Error sending stream from RP: {e}")
        except Exception as e:
            print(f"Error creating and sending the packet from RP: {e}")

    def rmvClient(self, client_ip):
        try:
            for track in self.Node_Track:
                if client_ip in track[1]:
                    new_track = splitTracks(track[1], client_ip)
                    if new_track:
                        self.Node_Track.append((track[0], new_track))
                    self.Node_Track.remove(track)
                    break
        
        except Exception as e:
            print("Erro ao remover o caminho para o cliente que deu dsiconnect: ", e)