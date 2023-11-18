import tkinter as tk
import socket
import threading
from PIL import ImageTk
from Packet import *
from NodeData import *

class ClienteGUI:

    def __init__(self, node):
        self.node = node
        self.streansNoRP = None
        self.rp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.condition = threading.Condition()
        self.conditionBool = False
        self.status = "Playing"
        self.packetQueue = []
        self.clientStart()
        
    def clientStart(self):
        try:
            self.inicialConnection()
            self.askStreamTransmission()
            thread = threading.Thread(target=self.streamTransmission())
            thread.start()
            thread.join()
        except Exception as e:
            print(e)
            
    def inicialConnection(self):
        #conectar ao servidor 
        rp_address = NodeData.getRPAddress(self.node)
        cliente_address = (NodeData.getIp(self.node), 0)
        try:
            self.rp_socket.bind(cliente_address)
            self.rp_socket.connect(rp_address)
    
            #pedir os videos que ele tem 
            message = "VideoList"
            self.rp_socket.sendall((message).encode())
            #receber a lista de video do rp
            data = self.rp_socket.recv(1024)
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
        try:
            mensagem = f"Stream- {video}"
            self.rp_socket.sendall((mensagem).encode())
            with self.condition:
                self.conditionBool = True
                self.condition.notify()
        finally:
            self.janela.destroy()
            self.rp_socket.close()
    
    def waitselction(self):
        with self.condition:
            print("waiting")
            self.condition.wait()
    
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
        my_address = (NodeData.getIp(self.node), NodeData.getStreamPort(self.node))
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as socketForStream:
            try:
                socketForStream.bind(my_address)
                print(f"{my_address} à espera de conexões de Streams: ")
                while not self.status == "Closed":
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
        self.status = "Closed"
        self.janela.destroy()
    
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