from PIL import Image, ImageTk
import cv2, imutils, socket
import numpy as np
import time, os
import base64
import threading, wave, pyaudio,pickle,struct
import tkinter as tk

class Cliente():
	def __init__(self):
		self.janela = tk.Tk()
		self.janela.title("Cliente")
        
        # Substitui o Canvas por um Label
		self.label = tk.Label(self.janela, width=640, height=480, bg='white')
		self.label.pack()

		self.botaoClose = tk.Button(self.janela, width=20, padx=3, pady=3)
		self.botaoClose["text"] = "Close"
		self.botaoClose.pack(padx=2, pady=2)

		self.host_ip = "127.0.0.1"
		self.porta = 12345
		self.BUFF_SIZE = 65536
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.BREAK = False
		self.receive_video = True
		self.photo = None

		self.main()

	def receive_video_thread(self):
		while self.receive_video:
			try:
				# Recebe o tamanho do frame (4 bytes) do servidor
				frame_size_bytes = self.server_socket.recv(4)
				frame_size = int.from_bytes(frame_size_bytes, byteorder='big')

				# Recebe o frame do servidor
				frame_data = b""
				while len(frame_data) < frame_size:
					frame_data += self.server_socket.recv(frame_size - len(frame_data))

				# Converte os dados do frame em uma imagem
				img = ImageTk.PhotoImage(data=frame_data)

				# Atualiza a label na janela Tkinter com a nova imagem
				self.label.configure(image=img)
				self.label.image = img
				self.janela.update()
			except Exception as e:
                # Registre a exceção para fins de depuração
				print(f"Erro ao receber vídeo: {e}")
		
		'''
	def convert_to_photo_image(self, frame):
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		frame = cv2.resize(frame, (640, 480))
		photo = Image.fromarray(frame)
		self.photo = ImageTk.PhotoImage(image=photo)
	'''
	def recibeAudio(self):
		p = pyaudio.PyAudio()
		CHUNK = 1024
		stream = p.open(format=p.get_format_from_width(2),
						channels=2,
						rate=44100,
						output=True,
						frames_per_buffer=CHUNK)
						
		# create socket
		client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		socket_address = (self.host_ip,self.porta-1)
		print('server listening at',socket_address)
		client_socket.connect(socket_address) 
		print("CLIENT CONNECTED TO",socket_address)
		data = b""
		payload_size = struct.calcsize("Q")
		while True:
			try:
				while len(data) < payload_size:
					packet = client_socket.recv(4*1024) # 4K
					if not packet: break
					data+=packet
				packed_msg_size = data[:payload_size]
				data = data[payload_size:]
				msg_size = struct.unpack("Q",packed_msg_size)[0]
				while len(data) < msg_size:
					data += client_socket.recv(4*1024)
				frame_data = data[:msg_size]
				data  = data[msg_size:]
				frame = pickle.loads(frame_data)
				stream.write(frame)
			except:
				break
		client_socket.close()
		print('Audio closed',self.BREAK)
		os._exit(1)

	def initialCon(self):
		socket_address = (self.host_ip, self.porta)
		self.server_socket.connect(socket_address)
		print("Cliente connectado: ", socket_address)

	def main(self):
		self.initialCon()
		t1 = threading.Thread(target=self.receive_video_thread)
		t2 = threading.Thread(target=self.recibeAudio)
		t1.start()
		t2.start()
		self.janela.mainloop()
		

if __name__ == "__main__":
    cliente = Cliente()
    cliente.janela.mainloop()