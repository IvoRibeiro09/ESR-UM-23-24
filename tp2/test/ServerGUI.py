import socket, cv2, pickle, struct
import imutils
import cv2
import threading
from tkinter import *
from PIL import Image, ImageTk

class ServerGUI:
	
	# Initiation..
    def __init__(self, janela, RP_IP, porta):
        self.janela = janela
        self.rp_ip = RP_IP
        self.rp_porta = int(porta)
        self.streamInterface()   
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_address = (self.rp_ip, self.rp_porta)
        

    def streamInterface(self):
        # Criar a tela de reprodução
        self.tela = Label(self.janela, height= 20)
        self.tela.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5)

        # Butao de menu para futuras alterações 
        self.botaoSetup = Button(self.janela, width=20, padx=3, pady=3)
        self.botaoSetup["text"] = "Setup Menu"
        self.botaoSetup["command"] = self.setupMovie
        self.botaoSetup.grid(row=1, column=0, padx=2, pady=2)
        
        # Butao streamar e enviar a stream de video para o cliente		
        self.botaoStart = Button(self.janela, width=20, padx=3, pady=3)
        self.botaoStart["text"] = "Play"
        self.botaoStart["command"] = self.playMovie
        self.botaoStart.grid(row=1, column=1, padx=2, pady=2)
        
        # Butao pausa de enviar a stream de video para o cliente				
        self.botaoPause = Button(self.janela, width=20, padx=3, pady=3)
        self.botaoPause["text"] = "Pause"
        self.botaoPause["command"] = self.pauseMovie
        self.botaoPause.grid(row=1, column=2, padx=2, pady=2)
            
        # Para de streamar o video
        self.botaoClose = Button(self.janela, width=20, padx=3, pady=3)
        self.botaoClose["text"] = "Close"
        self.botaoClose["command"] =  self.exitClient
        self.botaoClose.grid(row=1, column=3, padx=2, pady=2)


    def setupMovie(self):
        print("Conectar ao RP")
        self.client_socket.connect(self.client_address)
        print("Servidor connectado ao RP: ", self.client_address)

    def playMovie(self):
        print("Streaming")
        # abrir o ficheiro de streaming
        video_stream = cv2.VideoCapture("../VIDEO/video.mp4")
        if not video_stream.isOpened():
            print("Não é possivel abrir o ficheiro que pretende streamar!!!")
    
        while video_stream.isOpened():
            image, frame = video_stream.read()
            if not image:
                break
            
            # redimensionar o quadro para uma largura de 320 pixels 
            frame = imutils.resize(frame, width=320)
            # O quadro é serializado em bytes para ser enviado
            a = pickle.dumps(frame)
            message = struct.pack("Q", len(a))+a
            self.client_socket.sendall(message)

            # stream no servidor ao vivo caquilo que ele esta a streamar
            cv2.imshow("TRANSMITTING TO CACHE SERVER",frame)
            # Convert the OpenCV frame to a PhotoImage to display in the Label widget
            '''
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame)
            photo = ImageTk.PhotoImage(image=pil_image)  # Create PhotoImage from the PIL Image

            self.tela.config(image=photo)
            self.tela.image = photo
'''
            # forçar fechar a janela
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.client_socket.close()
                break

    def pauseMovie():
        print("ola")

    def exitClient():
        print("exit")