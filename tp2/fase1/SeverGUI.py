import socket, os

class ServerGUI:

    def __init__(self,ip , ip_rp, porta_rp):
        self.ip = ip 
        self.ipDoRP = ip_rp
        self.portaDoRP = porta_rp
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (self.ipDoRP, self.portaDoRP)
        self.videoList = []
        self.serverStarter()

    def parse(self):
        print("Parsing server...")
        # ao fazer parse do ficheiro guardar o nome e o caminho para o ficheiro
        # (Nome , caminho)
        video1 = "../VIDEO/video.mp4"
        video2 = "../VIDEO/videoA.mp4"
        
        self.videoList.append((getVideoName(video1), video1))
        self.videoList.append((getVideoName(video2), video2))
        print(self.videoList)

    def serverStarter(self):
        print("Starter...")
        self.parse()
        self.conectToRP()
    
    def conectToRP(self):
        try:
            self.server_socket.connect(self.server_address)
            print("Servidor conectado ao RP")

            # enviar os videos que você tem para exibir
            for video in self.videoList:
                msg = f"ADD-{video[0]}".encode('utf-8')
                self.server_socket.sendall(msg)

            # enviar mensagem de que já enviou tudo
            end_msg = "-END".encode('utf-8')
            self.server_socket.sendall(end_msg)

            print("RP informado dos vídeos que o servidor tem disponíveis...")
        except Exception as e:
            print(f"Erro ao conectar ou enviar mensagens: {e}")


def getVideoName(video):
    # nome do ficheiro sem o caminho
    nomeExtensao = os.path.basename(video)
    video_sem_extensao, extensao = os.path.splitext(nomeExtensao)
    return video_sem_extensao
    

if __name__ == "__main__":
    try:
        ip = '127.0.0.2'
        porta_rp = 12346
        ip_rp = '127.0.0.1' 

        # Criar um Servidor
        rp = ServerGUI(ip, ip_rp, porta_rp)
    except:
        print("[Usage: Server.py]\n")	