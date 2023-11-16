import socket 
import threading
import queue
import time
import cv2
import tkinter as tk
from PIL import ImageTk
from Packet import *
from NodeData import *
BUFFER_SIZE = 110000
#class Stream:

class ServerGUI:

    def __init__(self, node):
        self.node = node
        # Inicializa a janela Tkinter
        self.janela = tk.Tk()
        self.janela.geometry("+100+50")
        self.janela.title("Video Stream Client")
        self.label = tk.Label(self.janela)
        self.label.pack()
        self.streaming_streams = []
        self.serverStarter()

    def serverStarter(self):
        print("Starter...")
        self.conectToRP()
        self.receberPedidos()
        
    def conectToRP(self):
        server_address = (NodeData.getIp(self.node),0)
        rp_address = (NodeData.getRPAddress(self.node))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as rp_socket:
            try:
                rp_socket.bind(server_address)
                rp_socket.connect(rp_address)
                print("Servidor conectado ao RP")
        
                # enviar os videos que você tem para exibir
                msg = ""
                for stream in NodeData.getStreamList(self.node):
                    msg += f"{stream[0]}-AND-"

                msg = msg[:-5] 
                data = msg.encode('utf-8')
                rp_socket.sendall(data)
                print(msg)
                print("RP informado dos vídeos que o servidor tem disponíveis...")
            except Exception as e:
                print(f"Erro ao conectar ou enviar mensagens: {e}")
            finally:
                rp_socket.close()

    def receberPedidos(self):
        print("Server à espera de pedidos de Stream do RP")
        socket_address = (NodeData.getIp(self.node), 12346)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            try:
                server_socket.bind(socket_address)
                server_socket.listen(1)
                while True:
                    conn, addr = server_socket.accept()
                    data = conn.recv(1024)
                    if not data:
                        break
                    mensagem = data.decode('utf-8')
                    if "Stream- " in mensagem:
                        self.streaming_streams.append(extrair_texto(mensagem))
                        thread = threading.Thread(target=self.sendStream)
                        thread.start()
                        self.janela.mainloop()
                    conn.close()
            except Exception as e:
                print(f"Erro ao receber mensagens do RP: {e}")
            finally:
                server_socket.close()

    def sendStream(self):
        streamName = self.streaming_streams.pop()
        print(f"Vou streamar o video: {streamName}")
        streampath = None
        for video in NodeData.getStreamList(self.node):
            if video[0] == streamName:
                streampath = video[1]
        if streampath:
            rp_address = (NodeData.getRPAddress(self.node)[0], NodeData.getStreamPort(self.node))
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as stream_socket:
                try:
                    #stream_socket.bind(server_address)
                    sstream = cv2.VideoCapture(streampath)
                    fps =  sstream.get(cv2.CAP_PROP_FPS)
                    frame_interval = 1.0 / fps
                    st = time.time()
                    i = 0
                    while sstream.isOpened():
                        print("Frame: ",i)
                        ret, frame = sstream.read()
                        if not ret:break
                        
                        text = f"Server Frame: {i}"
                        pacote = Packet(streamName, text)
                        pacote_data = pacote.buildPacket()
                        stream_socket.sendto(pacote_data, rp_address)
                        
                        # Calcule o tempo decorrido desde o último envio
                        elapsed_time = time.time() - st

                        # Aguarde o tempo restante para manter a taxa de quadros
                        time.sleep(max(0, frame_interval - elapsed_time))

                        st = time.time()
                        '''
                        # Converte os dados do frame em uma imagem
                        img = ImageTk.PhotoImage(data=Packet.getFrameData(pacote))

                        # Atualiza a label na janela Tkinter com a nova imagem
                        self.label.configure(image=img)
                        self.label.image = img
                        self.janela.update()
                        '''
                        i+=1
                    print('Player closed')
                except Exception as e:
                    print(f"Erro ao Streamar para o RP: {e}")
                finally:
                    stream_socket.close()