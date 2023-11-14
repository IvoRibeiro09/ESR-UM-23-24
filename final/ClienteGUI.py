import tkinter as tk
import socket
import threading
from PIL import ImageTk
from Packet import *
from NodeData import *

class ClienteGUI:

    def __init__(self, node):
        self.node = node
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.streansNoRP = None
        self.condition = threading.Condition()
        self.conditionBool = False
        self.status = "Playing"
        self.clientClose = True
        self.clientStart()
        
    def clientStart(self):
        try:
            print("Starter...")
            self.inicialConnection()
            self.askStreamTransmission()
            thread = threading.Thread(target=self.streamTransmission())
            thread.start()
            thread.join()
        except Exception as e:
            print(e)
            
    def inicialConnection(self):
        #conectar ao servidor 
        socket_address = NodeData.getRPAddress(self.node)
        self.server_socket.connect(socket_address)
        #pedir os videos que ele tem 
        try:
            message = "VideoList"
            self.server_socket.sendall((message).encode())
            #receber a lista de video do rp
            data = self.server_socket.recv(1024)
            mensagem = data.decode()
            vids = mensagem.split("/")
            vids.pop()
            self.streansNoRP = vids
            print("Pedido de quais videos exixtem no RP recebido")
        except Exception as e:
            print(f"Erro ao conectar ou enviar mensagens: {e}")

    def askStreamTransmission(self):
        self.clienteInterface()
        with self.condition:
            while not self.conditionBool:
                self.condition.wait()
        self.conditionBool = False

    def clienteInterface(self):
        self.janela = tk.Tk()
        self.janela.title(f"Cliente {NodeData.getIp(self.node)}")
        self.janela.geometry("+1000+50")
        print("Show interface1...")
        i = 0
        spacing = 10
        for stream in self.streansNoRP:
            #tela com nome
            self.label = tk.Label(self.janela, width=60, padx=spacing, pady=spacing)
            self.label["text"] = f"{stream}"
            self.label.grid(row=i, column=0, padx=spacing, pady=spacing)

            # Botao streamar e enviar a stream de video para o cliente		
            self.botaoStart = tk.Button(self.janela, width=30, padx=spacing, pady=spacing)
            self.botaoStart["text"] = "Select"
            self.botaoStart["command"] = lambda s=stream: self.selectStream(s)
            self.botaoStart.grid(row=i, column=1, padx=spacing, pady=spacing)
            i+=1
        self.janela.mainloop()

    def selectStream(self, video):
        print(f"{video} has been selected...")
        mensagem = f"Stream- {video}"
        self.server_socket.sendall((mensagem).encode())
        with self.condition:
            self.conditionBool = True
            self.condition.notify()
        self.janela.destroy()
    
    def waitselction(self):
        with self.condition:
            print("waiting")
            self.condition.wait()
    
    def streamTransmission(self):
        print("Cliente aguarda video...")
        '''
        self.janela = tk.Tk()
        self.janela.title(f"Cliente {NodeData.getIp(self.node)}")
        self.janela.geometry("+1000+50")
        
        # tela de display de video
        self.label = tk.Label(self.janela, width=640, height=480, bg='white')
        self.label.grid(row=0, column=0, padx=10, pady=10, columnspan=2)


        # Butao pausa de enviar a stream de video para o cliente				
        self.botaoPause = tk.Button(self.janela, width=20, padx=3, pady=3)
        self.botaoPause["text"] = "Pause"
        self.botaoPause["command"] = self.pauseStream
        self.botaoPause.grid(row=1, column=0, padx=10, pady=10)

        # Para de streamar o video
        self.botaoClose = tk.Button(self.janela, width=20, padx=3, pady=3)
        self.botaoClose["text"] = "Close"
        self.botaoClose["command"] =  self.closeStream
        self.botaoClose.grid(row=1, column=1, padx=10, pady=10)
        '''
        # recebe o video em bytes do cliente
        i = 0
        socket_address = (NodeData.getIp(self.node), NodeData.getStreamPort(self.node))
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as socketForStream:
            try:
                socketForStream.connect(socket_address)
                print(f"{socket_address} à espera de conexões de Streams: ")
                i=0
                while True:
                    #parse packet | Recebe o tamanho do frame (4 bytes) do servidor
                    allpacket_size = socketForStream.recv(4)
                    print("Frame: ", i)
                    packet_size = int.from_bytes(allpacket_size, byteorder='big')
                    
                    # Recebe o pacote do servidor
                    pacote_data = b""
                    pacote_data += allpacket_size
                    while len(pacote_data) < packet_size + 4:
                        pacote_data += socketForStream.recv(packet_size + 4 - len(pacote_data))

                    pacote = Packet()
                    Packet.parsePacket(pacote, pacote_data)
                    print("msg no pacote: ",Packet.getFrameData(pacote).decode('utf-8'))
                    '''
                    if self.status == "Playing":
                        # Converte os dados do frame em uma imagem
                        img = ImageTk.PhotoImage(data= Packet.getFrameData(pacote))

                        # Atualiza a label na janela Tkinter com a nova imagem
                        self.label.configure(image=img)
                        self.label.image = img
                        #self.janela.update()
                    self.janela.update()
                    '''
                    i+=1

            except Exception as e:
                print(f"Erro ao receber vídeo: {e}")
            finally:
                socketForStream.close()

    def pauseStream(self):
        if self.status == "Playing":
            print("Stream paused...")
            self.status = "Pause"
            self.botaoPause["text"] = "Resume"
        elif self.status == "Pause":
            print("Stream resumed...")
            self.status = "Playing"
            self.botaoPause["text"] = "Pause"

    def closeStream(self):
        print("Closing Stream...")
        self.server_socket.close()
        self.janela.destroy()
    
    def clinetNewStart(self):
        self.janela = tk.Tk()
        self.janela.title(f"Cliente {self.IP}")
        spacing = 10
        #tela
        self.label = tk.Label(self.janela, width=60, padx=spacing, pady=spacing)
        self.label["text"] = "Transmission has ended!!!\nWant to continue watching a new Stream..."
        self.label.grid(row=0, column=0, padx=spacing, pady=spacing, columnspan=2)

        # Botao streamar e enviar a stream de video para o cliente		
        self.botaoStart = tk.Button(self.janela, width=30, padx=spacing, pady=spacing)
        self.botaoStart["text"] = "Yes"
        self.botaoStart["command"] = self.yesbutton
        self.botaoStart.grid(row=1, column=0, padx=spacing, pady=spacing)
	
        self.botaoStart = tk.Button(self.janela, width=30, padx=spacing, pady=spacing)
        self.botaoStart["text"] = "No"
        self.botaoStart["command"] = self.nobutton
        self.botaoStart.grid(row=1, column=1, padx=spacing, pady=spacing)
        self.janela.mainloop()

    def yesbutton(self):
        global OnOff
        OnOff = True
        self.conditionBool = True
        with self.condition:
            self.condition.notify()
        self.janela.destroy()

    def nobutton(self):
        global OnOff
        OnOff = False
        self.conditionBool = True
        with self.condition:
            self.condition.notify()
        self.janela.destroy()
    