import socket
import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk

# Configurações do servidor
HOST = '127.0.0.1'  # Endereço IP do servidor
PORT = 12345  # Porta do servidor
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Inicializa a janela Tkinter
root = tk.Tk()
root.title("Video Stream Server")

# Inicializa uma label para exibir os frames recebidos
label = tk.Label(root)
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
cap = cv2.VideoCapture('../VIDEO/video.mp4')

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
    img = ImageTk.PhotoImage(data=frame_data)
    label.config(image=img)
    label.image = img

# Fecha as conexões e a janela Tkinter quando o loop termina
cap.release()
client_socket.close()
server_socket.close()
root.destroy()
