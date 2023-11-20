import socket 
import threading
import time
import cv2
import tkinter as tk
from PIL import ImageTk
from Packet import *
from NodeData import *

class ServerGUI:

    def __init__(self, node):
        self.node = node
        self.streamList = {}
        self.serverStarter()

    def serverStarter(self):
        self.conectToRP()
        self.receberPedidos()
        
    def conectToRP(self):
        server_address = (NodeData.getIp(self.node),0)
        rp_address = (NodeData.getRPAddress(self.node))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as rp_socket:
            try:
                rp_socket.bind(server_address)
                rp_socket.connect(rp_address)
        
                # enviar os videos que você tem para exibir
                msg = ""
                for stream in NodeData.getStreamList(self.node).keys():
                    msg += f"{stream}-AND-"

                msg = msg[:-5] 
                data = msg.encode('utf-8')
                rp_socket.sendall(data)

                print("Server conected to RP")
            except Exception as e:
                print(f"Erro ao conectar ou enviar mensagens: {e}")
            finally:
                rp_socket.close()

    def receberPedidos(self):
        print("Server waiting Stream requests")
        socket_address = (NodeData.getIp(self.node), 12346)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            try:
                server_socket.bind(socket_address)
                server_socket.listen()
                while True:
                    conn, addr = server_socket.accept()
                    data = conn.recv(1024)
                    if not data:break
                    mensagem = data.decode('utf-8')
                    if "Start Stream- " in mensagem:
                        stream_name = extrair_texto(mensagem)
                        self.streamList[stream_name] = "Asked"
                        thread = threading.Thread(target=self.startStream)
                        thread.start()
                    elif "Close Stream- " in mensagem:
                        stream_to_close = extrair_texto(mensagem)
                        self.closeStream(stream_to_close)
                    else:
                        print(mensagem)
                        
                    conn.close()
            except Exception as e:
                print(f"Erro ao receber mensagens do RP: {e}")
            finally:
                server_socket.close()

    def startStream(self):
        streamName = None
        for s in self.streamList.keys():
            if self.streamList[s] == "Asked":
                streamName = s
        self.streamList[streamName] = "Streaming"
        print(f"Streaming: {streamName}")
        streampath = NodeData.getStreamList(self.node)[streamName]
        rp_address = (NodeData.getRPAddress(self.node)[0], NodeData.getStreamPort(self.node))
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as stream_socket:
            try:
                sstream = cv2.VideoCapture(streampath)
                fps =  sstream.get(cv2.CAP_PROP_FPS)
                frame_interval = 1.0 / fps
                st = time.time()
                i=0
                while sstream.isOpened() and self.streamList[streamName] != "Closed":
                    ret, frame = sstream.read()
                    if not ret:break

                    Frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
                    frame_data = cv2.imencode('.jpg', Frame)[1].tobytes()
                    # Obtenha o comprimento total dos dados
                    total_length = len(frame_data)
                    
                    split_point1 = total_length // 3
                    split_point2 = 2 * total_length // 3

                    # Divida os dados
                    data_part1 = frame_data[:split_point1]
                    data_part2 = frame_data[split_point1:split_point2]
                    data_part3 = frame_data[split_point2:]
                    
                    #text = f"Server Frame: {i} of {streamName}"
                    pacote = Packet(streamName, i, data_part1)
                    pacote_data = pacote.buildPacket()
                    stream_socket.sendto(pacote_data, rp_address)
                    pacote = Packet(streamName, i, data_part2)
                    pacote_data = pacote.buildPacket()
                    stream_socket.sendto(pacote_data, rp_address)
                    pacote = Packet(streamName, i, data_part3)
                    pacote_data = pacote.buildPacket()
                    stream_socket.sendto(pacote_data, rp_address)
                    
                    # Calcule o tempo decorrido desde o último envio
                    elapsed_time = time.time() - st

                    # Aguarde o tempo restante para manter a taxa de quadros
                    time.sleep(max(0, frame_interval - elapsed_time))

                    st = time.time()
                    print("Frame: ",i)
                    i+=1
                if self.streamList[streamName] == "Streaming":
                    self.closeStream(streamName)

            except Exception as e:
                print(f"Erro ao Streamar para o RP: {e}")
            finally:
                stream_socket.close()

    def closeStream(self, stream):
        self.streamList[stream] = "Closed"
        print(f"{stream} closed!")
