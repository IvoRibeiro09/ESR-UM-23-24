# This is server code to send video and audio frames over UDP/TCP

import cv2, imutils, socket
import numpy as np
import time
import base64
import threading, wave, pyaudio, pickle, struct
import queue, os
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk

class ServerGUI:
	
	# Initiation..
    def __init__(self, janela, RP_IP, porta):
        self.janela = janela
        self.rp_ip = RP_IP
        self.rp_porta = int(porta)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_address = (self.rp_ip, self.rp_porta)
        self.queue = queue.Queue(maxsize=1)
        self.filename = ["../VIDEO/video.mp4", "../VIDEO/videoA.mp4", "../VIDEO/videoB.mp4"]
        self.BUFFER_SIZE = 65536
        self.client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,self.BUFFER_SIZE)
        self.videoToStream = cv2.VideoCapture("../VIDEO/video.mp4")
        self.FPS = self.videoToStream.get(cv2.CAP_PROP_FPS)
        self.TS = 0.5/self.FPS
        self.current_image = None
        self.Pause = False
        self.serverInterface()
        #self.streamInterface()

    # command = "ffmpeg -i {} -ab 160k -ac 2 -ar 44100 -vn {}".format(filename,'temp.wav')
    # os.system(command)
    def serverInterface(self):
        i = 0
        for file in self.filename:
            print(file)
            self.tela = Label(self.janela, width=40, height=10)
            self.tela["text"] = file
            self.tela.grid(row=i, column=0, padx=5, pady=5)
            # Butao streamar e enviar a stream de video para o cliente		
            self.botaoStart = Button(self.janela, width=20, padx=3, pady=3)
            self.botaoStart["text"] = "Select"
            self.botaoStart["command"] = self.selectStream
            self.botaoStart.grid(row=i, column=1, padx=2, pady=2)
            i+=1

    def selectStream(self):
        # Butao de menu para futuras alterações 
        self.botaoSetup = Button(self.janela, width=20, padx=3, pady=3)
        self.botaoSetup["text"] = "Setup Menu"
        self.botaoSetup["command"] = self.setupMovie
        self.botaoSetup.grid(row=0, column=0, padx=2, pady=2)
        
        # Butao streamar e enviar a stream de video para o cliente		
        self.botaoStart = Button(self.janela, width=20, padx=3, pady=3)
        self.botaoStart["text"] = "Play"
        self.botaoStart["command"] = self.playMovie
        self.botaoStart.grid(row=0, column=1, padx=2, pady=2)
        
        # Butao pausa de enviar a stream de video para o cliente				
        self.botaoPause = Button(self.janela, width=20, padx=3, pady=3)
        self.botaoPause["text"] = "Pause"
        self.botaoPause["command"] = self.pauseMovie
        self.botaoPause.grid(row=0, column=2, padx=2, pady=2)
            
        # Para de streamar o video
        self.botaoClose = Button(self.janela, width=20, padx=3, pady=3)
        self.botaoClose["text"] = "Close"
        self.botaoClose["command"] =  self.exitClient
        self.botaoClose.grid(row=0, column=3, padx=2, pady=2)

    def streamInterface(self):
        # Criar a tela de reprodução
        self.tela = Label(self.janela, width=60, height=40)
        self.tela.grid(row=0, column=0, columnspan=4, sticky="wens", padx=5, pady=5)
        

        # Butao de menu para futuras alterações 
        self.botaoSetup = Button(self.janela, width=20, padx=3, pady=3)
        self.botaoSetup["text"] = "conectar ao RP"
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
        # message = b'Hello'
        # self.client_socket.sendto(message,(self.rp_ip, self.rp_porta))
        
    
    def pauseMovie(self):
        print("Pause")
        if not self.Pause:
            self.botaoPause["Text"] = "Resume"
            self.Pause = True
        else:
            self.botaoPause["Text"] = "Pause"
            self.Pause = False

    def exitClient():
        print("exit")   

    def playMovie(self):
        print("Streaming")
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=3) as executor:
            #executor.submit(self.audio_stream)
            executor.submit(self.video_stream_gen)
            executor.submit(self.video_stream)

    def video_stream_gen(self):
        WIDTH=400
        while(self.videoToStream.isOpened()):
            try:
                _,frame = self.videoToStream.read()
                frame = imutils.resize(frame,width=WIDTH)
                self.queue.put(frame)
            except:
                os._exit(1)
        print('Player closed')
        BREAK=True
        self.videoToStream.release()
	

    def video_stream(self):
        #global TS
        fps,st,frames_to_count,cnt = (0,0,1,0)
        WIDTH = 400
        i=0
        while True:
            #while True:
                frame = self.queue.get()
                encoded,buffer = cv2.imencode('.jpeg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
                message = base64.b64encode(buffer)                
                self.client_socket.sendto(message,self.client_address)
                #frame = cv2.putText(frame,'FPS: '+str(round(fps,1)),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
                if cnt == frames_to_count:
                    try:
                        fps = (frames_to_count/(time.time()-st))
                        st=time.time()                        
                        cnt=0
                        if fps>self.FPS:
                            self.TS+=0.001
                        elif fps<self.FPS:
                            self.TS-=0.001
                        else:
                            pass
                    except:
                        pass
                cnt+=1
                # stream no servidor ao vivo caquilo que ele esta a streamar
                cv2.imshow('TRANSMITTING VIDEO', frame)
                
                # Display the frame in a custom GUI window
                '''
                    try:
                        frame_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        frame_image = Image.fromarray(frame_image)
                        frame_image = ImageTk.PhotoImage(image=frame_image)

                        self.tela.config(image=frame_image, width=60, height=40)
                        self.tela.image = frame_image
                    except:
                        pass
                '''
                key = cv2.waitKey(int(1000*self.TS)) & 0xFF	
                if key == ord('q'):
                    os._exit(1)
                    TS=False
                    break	
                                    
    '''
    def audio_stream():
        s = socket.socket()
        s.bind((host_ip, (port-1)))

        s.listen(5)
        CHUNK = 1024
        wf = wave.open("../VIDEO/temp.wav", 'rb')
        p = pyaudio.PyAudio()
        print('server listening at',(host_ip, (port-1)))
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
    '''