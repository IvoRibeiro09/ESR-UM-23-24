import socket
import cv2
import tkinter as tk
from PIL import Image, ImageTk

# Configurações do cliente
HOST = '127.0.0.1'  # Endereço IP do servidor
PORT = 12345  # Porta do servidor

# Inicializa a janela Tkinter
root = tk.Tk()
root.title("Video Stream Client")

# Inicializa uma label para exibir os frames recebidos
label = tk.Label(root)
label.pack()

# Inicializa a conexão com o servidor
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
print(f"Conectado ao servidor em {HOST}:{PORT}")

while True:
    # Recebe o tamanho do frame (4 bytes) do servidor
    frame_size_bytes = client_socket.recv(4)
    frame_size = int.from_bytes(frame_size_bytes, byteorder='big')

    # Recebe o frame do servidor
    frame_data = b""
    while len(frame_data) < frame_size:
        frame_data += client_socket.recv(frame_size - len(frame_data))

    # Converte os dados do frame em uma imagem
    img = ImageTk.PhotoImage(data=frame_data)

    # Atualiza a label na janela Tkinter com a nova imagem
    label.config(image=img)
    label.image = img
    root.update()

# Fecha a conexão e a janela Tkinter quando o loop termina
client_socket.close()
root.destroy()
