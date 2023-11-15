import cv2
import pickle

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

class Packet:
    def __init__(self, name, Frame, i):
        self.name_data = name.encode('utf-8') 
        self.name_size = len(self.name_data)
        Frame = cv2.resize(Frame, (FRAME_WIDTH, FRAME_HEIGHT))
        frame_data = cv2.imencode('.jpg', Frame)[1].tobytes()
        text =  f"Server Frame: {i}"
        self.frame_data = text.encode('utf-8')
        self.frame_size = len(self.frame_data)
        self.total_size = 4 + 4 + self.name_size + 4 + self.frame_size

    # getterss
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
    def __init__(self, caminho, frame):
        self.track_data = caminho.encode('utf-8') 
        self.track_size = len(self.track_data)
        self.frame_data = frame
        self.frame_size = len(self.frame_data)
        self.total_size = 4 + 4 + self.track_size + 4 + self.frame_size

    def buildTrackedPacket(self):
        packet_data = (
            self.total_size.to_bytes(4, byteorder='big') +
            self.track_size.to_bytes(4, byteorder='big') +
            self.track_data +
            self.frame_size.to_bytes(4, byteorder='big') +
            self.frame_data 
        )
        return packet_data