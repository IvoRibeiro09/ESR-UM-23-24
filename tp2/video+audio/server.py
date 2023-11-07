import cv2, imutils, socket
import numpy as np
import time
import base64
import threading, wave, pyaudio,pickle,struct
import sys
import queue
import os
from PIL import Image, ImageTk    
import tkinter as tk     
        
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS_TARGET = 24

class Server():
    def __init__(self):
        self.IP = "127.0.0.1"
        self.porta = 12345
        self.BUFF_SIZE = 65536
        self.filename = '../VIDEO/video.mp4'
        self.audiofile = None
        self.getaudiofile()
        # Inicializa a janela Tkinter
        self.janela = tk.Tk()
        self.janela.title("Video Stream Client")

        # Inicializa uma label para exibir os frames recebidos
        self.label = tk.Label(self.janela)
        self.label.pack()

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.BUFF_SIZE)
        self.socket_address = (self.IP, self.porta)
        self.client_socket = None
        self.client_address = None
        self.vid = cv2.VideoCapture(self.filename)
        self.q = queue.Queue(maxsize=10)
        self.FPS = self.vid.get(cv2.CAP_PROP_FPS)
        self.TS = (0.5/self.FPS)
        self.BREAK = False
        self.start()
        
    def getaudiofile(self):
        partes = self.filename.split('.')
        partes.pop()
        nome_sem_extensao = '.'.join(partes)
        self.audiofile = nome_sem_extensao+"temp.wav"
        if not os.path.exists(self.audiofile):   
            command = f"ffmpeg -i {self.filename} -ab 160k -ac 2 -ar 44100 -vn {self.audiofile}"
            os.system(command)

    def start(self):
        self.server_socket.bind(self.socket_address)
        self.server_socket.listen()
        print("Servidor à espera: ",self.socket_address)

        self.client_socket, self.client_address = self.server_socket.accept()
        print("Conexão aceite da", self.client_address)
        t1 = threading.Thread(target=self.video_stream2)
        t2 = threading.Thread(target=self.audio_stream)
        t1.start()
        t2.start()
        self.janela.mainloop()

    def video_stream2(self):
        #fps, st, frames_to_count, cnt = (0, 0, 1, 0)
        img = None  # Inicialize a variável de imagem fora do loop
        frame_rate = 24  # Taxa de quadros desejada (25 FPS)
        frame_interval = 1.0 / frame_rate
        st = time.time()
        while self.vid.isOpened():
            ret, frame = self.vid.read()
            if not ret:
                break

            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
            frame_data = cv2.imencode('.jpg', frame)[1].tobytes()

            frame_size = len(frame_data)
            self.client_socket.send(frame_size.to_bytes(4, byteorder='big'))
            self.client_socket.send(frame_data)

            
            # Calcule o tempo decorrido desde o último envio
            elapsed_time = time.time() - st

            # Aguarde o tempo restante para manter a taxa de quadros
            time.sleep(max(0, frame_interval - elapsed_time - 0.002))

            st = time.time()

            # Converte os dados do frame em uma imagem
            img = ImageTk.PhotoImage(data=frame_data)

			# Atualiza a label na janela Tkinter com a nova imagem
            self.label.configure(image=img)
            self.label.image = img
            self.janela.update()
        
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                os._exit(1)
                self.TS = False
                break

        print('Player closed')
        self.BREAK = True
        self.vid.release()

        '''
        import socket
import cv2
import numpy as np
import tkinter as tk
from tkinter import Label
from tkinter import PhotoImage

# Configurações do servidor
HOST = '127.0.0.1'  # Endereço IP do servidor
PORT = 12345  # Porta do servidor
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Inicializa a janela Tkinter
root = tk.Tk()
root.title("Video Stream Server")

# Inicializa uma label para exibir os frames recebidos
label = Label(root)
label.pack()

# Inicializa a conexão do servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print(f"Servidor aguardando conexão em {HOST}:{PORT}")

# Aceita a conexão do cliente
client_socket, client_address = server_socket.accept()
print(f"Cliente conectado: {client_address}")

# Inicializa a captura de vídeo (substitua '0' pelo índice da câmera se desejar capturar a partir de uma câmera)
cap = cv2.VideoCapture(0)

while True:
    # Captura um frame do vídeo
    ret, frame = cap.read()

    if not ret:
        break

    # Redimensiona o frame para o tamanho desejado
    frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

    # Converte o frame para um formato que pode ser transmitido via socket
    frame_data = cv2.imencode('.jpg', frame)[1].tobytes()

    # Envie o tamanho do frame e, em seguida, o frame em si para o cliente
    frame_size = len(frame_data)
    client_socket.send(frame_size.to_bytes(4, byteorder='big'))
    client_socket.send(frame_data)

    # Exibe o frame na janela Tkinter
    img = PhotoImage(data=frame_data)
    label.config(image=img)
    label.image = img

# Fecha as conexões e a janela Tkinter quando o loop termina
cap.release()
client_socket.close()
server_socket.close()
root.destroy()
'''

    def audio_stream(self):
        s = socket.socket()
        new_address = (self.IP, (self.porta-1))
        s.bind(new_address)

        s.listen(5)
        CHUNK = 1024
        wf = wave.open(self.audiofile, 'rb')
        p = pyaudio.PyAudio()
        print('server listening at',new_address)
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        input=True,
                        frames_per_buffer=CHUNK)
        client_socket,addr = s.accept()
        while True:
            if client_socket:
                while True:
                    data = wf.readframes(CHUNK)
                    a = pickle.dumps(data)
                    message = struct.pack("Q",len(a))+a
                    client_socket.sendall(message)


if __name__ == "__main__":
    server = Server()