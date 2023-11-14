import cv2
import pickle

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

class Packet:
    def __init__(self):
        self.total_size = None
        self.name_size = None
        self.name_data = None 
        self.frame_size = None
        self.frame_data = None
        
    def initial1(self, name, Frame):
        self.name_data = name.encode('utf-8') 
        self.name_size = len(self.name_data)
        Frame = cv2.resize(Frame, (FRAME_WIDTH, FRAME_HEIGHT))
        self.frame_data = cv2.imencode('.jpg', Frame)[1].tobytes()
        self.frame_size = len(self.frame_data)
        self.total_size = 4 + 4 + self.name_size + 4 + self.frame_size

    # getters
    def getTotalSize(self): 
        return self.total_size
    
    def getNameSize(self): 
        return self.name_size
    
    def getFrameSize(self): 
        return self.frame_size
    
    def getName(self):
        return self.name_data.decode('utf-8') 
    
    def getFrameData(self):
        return self.frame_data
    
    # setters
    def setTotalSize(self, size): 
        self.total_size = size

    def buildPacket(self):
        # Constrói o pacote com o tamanho total
        packet_data = (
            self.total_size.to_bytes(4, byteorder='big') +
            self.name_size.to_bytes(4, byteorder='big') +
            self.name_data +
            self.frame_size.to_bytes(4, byteorder='big') +
            self.frame_data 
        )
        return packet_data

    def parsePacket(self, data):
        self.total_size = int.from_bytes(data[0:4], byteorder='big')

        offset = 4
        self.name_size = int.from_bytes(data[offset:offset + 4], byteorder='big')

        offset += 4
        self.name_data = data[offset:offset + self.name_size]

        offset += self.name_size
        self.frame_size = int.from_bytes(data[offset:offset + 4], byteorder='big')

        offset += 4
        self.frame_data = data[offset:offset + self.frame_size]


class TrackedPacket:
    def __init__(self):
        self.total_size = None
        self.track_size = None
        self.track_data = None 
        self.frame_size = None
        self.frame_data = None

    def buildTrackedPacket(self, caminho):
        return b""