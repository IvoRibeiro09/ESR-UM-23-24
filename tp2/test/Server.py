import socket, cv2, pickle, struct
import imutils
import cv2
import threading
from tkinter import *
            
def startStream(client_socket, client_address):
    video_stream = cv2.VideoCapture("video.mp4")
    while video_stream.isOpened():
        image, frame = video_stream.read()

        frame = imutils.resize(frame, width=320)
        a = pickle.dumps(frame)
        message = struct.pack("Q", len(a))+a
        client_socket.sendall(message)
        cv2.imshow("TRANSMITTING TO CACHE SERVER",frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            client_socket.close()
            break
def setupMovie():
    print("ola")


def playMovie():
    print("ola")

def pauseMovie():
    print("ola")

def exitClient():
    print("exit")

def showInterface():
    janela = Tk()
    janela.title("Server Menu")
    #janela.createWidgets()
    """Build GUI."""
# Create Setup button
    janela.setup = Button(janela.master, width=20, padx=3, pady=3)
    janela.setup["text"] = "Menu"
    janela.setup["command"] = setupMovie
    janela.setup.grid(row=1, column=0, padx=2, pady=2)
		
	# Create Play button		
    janela.start = Button(janela.master, width=20, padx=3, pady=3)
    janela.start["text"] = "Play"
    janela.start["command"] = playMovie
    janela.start.grid(row=1, column=1, padx=2, pady=2)
		
	# Create Pause button			
    janela.pause = Button(janela.master, width=20, padx=3, pady=3)
    janela.pause["text"] = "Pause"
    janela.pause["command"] = pauseMovie
    janela.pause.grid(row=1, column=2, padx=2, pady=2)
		
	# Create Teardown button
    janela.teardown = Button(janela.master, width=20, padx=3, pady=3)
    janela.teardown["text"] = "Exit"
    janela.teardown["command"] =  exitClient
    janela.teardown.grid(row=1, column=3, padx=2, pady=2)
		
		# Create a label to display the movie
    janela.label = Label(janela.master, height=19)
    janela.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5)	
    janela.mainloop()

def main():
    host_ip = "127.0.0.1"   
    porta = 12346

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_address = (host_ip, porta)
    server_socket.bind(socket_address)
    server_socket.listen()

    # JANELA
    showInterface()
    
	
    print("Servidor à espera de conexão: ", socket_address)

    while True:
        client_socket, client_address = server_socket.accept()   # Aceita a conexão do cliente
    
        thread = threading.Thread(target=(startStream), args=(client_socket, client_address))
        thread.start()

if __name__ == "__main__":
    main()
 