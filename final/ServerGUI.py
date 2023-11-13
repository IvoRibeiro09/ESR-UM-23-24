import socket 
import threading
import queue
import time
import cv2
import tkinter as tk
from PIL import ImageTk
from connectionProtocol import *
from NodeData import *

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
        self.serverStarter()

    def serverStarter(self):
        print("Starter...")
        self.conectToRP()
        
    def conectToRP(self):
        server_address = (NodeData.getRPAddress(self.node))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as rp_socket:
            try:
                rp_socket.connect(server_address)
                print("Servidor conectado ao RP")
        
                # enviar os videos que você tem para exibir
                msg = ""
                for stream in NodeData.getStreamList(self.node):
                    msg += f"{stream[0]}-ADD-"

                msg = msg[:-5] 
                data = msg.encode()
                rp_socket.sendall(data)
                print(msg)
                print("RP informado dos vídeos que o servidor tem disponíveis...")

                print("Server à espera de pedidos de Stream do RP")
                while True:
                    data = rp_socket.recv(1024)
                    if not data:
                        break
                    mensagem = data.decode('utf-8')
                    if "Stream- " in mensagem:
                        thread = threading.Thread(target=self.sendStream, args=(extrair_texto(mensagem)))
                        thread.start()

            except Exception as e:
                print(f"Erro ao conectar ou enviar mensagens: {e}")
            finally:
                rp_socket.close()

    def sendStream(self, streamName):
        print(f"Vou streamar o video: {streamName}")
        streampath = None
        for video in NodeData.getStreamList(self.node):
            if video[0] == streamName:
                streampath = video[1]
        if streampath:
            sstream = cv2.VideoCapture(streampath)
            fps =  sstream.get(cv2.CAP_PROP_FPS)
            frame_interval = 1.0 / fps
            st = time.time()
            i = 0
            try:
                while sstream.isOpened():
                    print("Frame: ",i)
                    ret, frame = sstream.read()
                    if not ret:
                        break
                    
                    pacote = Packet()
                    pacote.initial1(streamName, frame)
                    self.server_socket.send(pacote.buildPacket())
                    
                    # Calcule o tempo decorrido desde o último envio
                    elapsed_time = time.time() - st

                    # Aguarde o tempo restante para manter a taxa de quadros
                    time.sleep(max(0, frame_interval - elapsed_time))

                    st = time.time()

                    # Converte os dados do frame em uma imagem
                    img = ImageTk.PhotoImage(data=pacote.frame_data)

                    # Atualiza a label na janela Tkinter com a nova imagem
                    self.label.configure(image=img)
                    self.label.image = img
                    self.janela.update()
                    i+=1
            finally:
                print('Player closed')