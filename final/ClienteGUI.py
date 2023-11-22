import tkinter as tk
import socket
import threading
from PIL import ImageTk
from Packet import *
from NodeData import *

class ClienteGUI:

    def __init__(self, node):
        self.node = node
        self.my_address = (NodeData.getIp(self.node), 0)
        self.selected = None
        self.condition = threading.Condition()
        self.conditionBool = False
        self.status = "Playing"
        self.packetQueue = []
        self.clientStart()
        
    def clientStart(self):
        try:
            while True:
                self.inicialConnection()
                self.streamTransmission()
        except Exception as e:
            print(e)
            
    def inicialConnection(self):
        #conectar ao servidor 
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as rp_socket:
                rp_socket.bind(self.my_address)
                rp_socket.connect(NodeData.getRPAddress(self.node))
        
                #pedir os videos que ele tem 
                message = "VideoList"
                rp_socket.sendall((message).encode())
                #receber a lista de video do rp
                data = rp_socket.recv(1024)
                mensagem = data.decode()
                vids = mensagem.split("/")
                vids.pop()
                
                self.askStreamTransmission(vids)
                mensagem = f"Stream- {self.selected}"
                rp_socket.sendall((mensagem).encode())
                
                print("Pedido de quais videos exixtem no RP recebido")
        except Exception as e:
            print(f"Erro ao conectar ou enviar mensagens: {e}")
        finally:
            rp_socket.close()

    def askStreamTransmission(self, streamList):
        self.clienteInterface(streamList)
        with self.condition:
            while not self.conditionBool:
                self.condition.wait()
        self.conditionBool = False

    def clienteInterface(self, streamList):
        self.janela = tk.Tk()
        self.janela.title(f"Cliente {NodeData.getIp(self.node)}")
        self.janela.geometry("+1000+50")
        
        i = 0
        spacing = 10
        for stream in streamList:
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
        self.janela.destroy()
        with self.condition:
            self.selected = video
            self.conditionBool = True
            self.condition.notify()
    
    def streamTransmission(self):
        print("Cliente aguarda video...")
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
        # recebe o video em bytes do cliente
        i = 0
        my_address_udp = (NodeData.getIp(self.node), NodeData.getStreamPort(self.node))
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as socketForStream:
                socketForStream.bind(my_address_udp)
                print(f"{my_address_udp} à espera de conexões de Streams: ")
                while self.status != "Closed":
                    #parse packet | Recebe o tamanho do frame (4 bytes) do servidor
                    data, _ = socketForStream.recvfrom(Packet_size)
                    pacote = Packet("", "", "")
                    Packet.parsePacket(pacote, data)
                    print("Frame: ", pacote.frameNumber)
                    if self.status == "Playing": self.packetQueue.append(pacote)

                    data1, _ = socketForStream.recvfrom(Packet_size)
                    pacote1 = Packet("", "", "")
                    Packet.parsePacket(pacote1, data1)
                    print("Frame: ", pacote1.frameNumber)
                    if self.status == "Playing": self.packetQueue.append(pacote1)

                    data2, _ = socketForStream.recvfrom(Packet_size)
                    pacote2 = Packet("", "", "")
                    Packet.parsePacket(pacote2, data2)
                    print("Frame: ", pacote2.frameNumber)
                    if self.status == "Playing": self.packetQueue.append(pacote2)
                    #print("msg no pacote: ",Packet.getFrameData(pacote))

                    if self.status == "Playing":
                        frame = self.verifyFrame()
                        if frame:
                            # Converte os dados do frame em uma imagem
                            img = ImageTk.PhotoImage(data= frame)

                            # Atualiza a label na janela Tkinter com a nova imagem
                            self.label.configure(image=img)
                            self.label.image = img   
                    self.janela.update()
        except Exception as e:
            print(f"Erro ao receber vídeo: {e}")
        finally:
            socketForStream.close()
            self.janela.destroy()
            self.status = "Playing"
            print("Closing Stream...")

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
        try:
            self.status = "Closed"
            self.rp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.rp_socket.bind(self.my_address)
            self.rp_socket.connect(NodeData.getRPAddress(self.node))
            #pedir os videos que ele tem 
            message = "Connection closed"
            self.rp_socket.sendall((message).encode())
            # o cliente avisa o rp que fechou a conexao
            
            print('The Client informed the RP that he no longer intends to receive the stream.')
        except Exception as e:
            print(f"Erro ao enviar mensagem de fechar a Stream para o servidor: {e}")
        finally:
            self.rp_socket.close()
            
    def verifyFrame(self):
        # verificar se os 3 elementos da lista sao do mesmo pacote
        pack1 = self.packetQueue[0]
        pack2 = self.packetQueue[1]
        pack3 = self.packetQueue[2]
        if Packet.getFrameNumber(pack1) == Packet.getFrameNumber(pack2) == Packet.getFrameNumber(pack3):
            self.packetQueue.pop(0)
            self.packetQueue.pop(0)
            self.packetQueue.pop(0)
            return Packet.getFrame(pack1) + Packet.getFrame(pack2) + Packet.getFrame(pack3)
        else:
            # se sim juntar e passar para imagem
            # caso contrario dar pop no primeiro pacote e se o len da queue for maior que tres verificar outra vez se sao o mesmo pacote
            print("nao coincide")
            self.packetQueue.pop(0)
            if len(self.packetQueue) >= 3:
                return self.verifyFrame()
            else:            
                return None