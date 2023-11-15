import cv2
import pickle

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

class Packet:
    def __init__(self, name, Frame):
        self.name_data = name
        #Frame = cv2.resize(Frame, (FRAME_WIDTH, FRAME_HEIGHT))
        #frame_data = cv2.imencode('.jpg', Frame)[1].tobytes()
        self.frame_data = Frame

    # getterss
    def getTotalSize(self): 
        return self.total_size
    
    def getNameData(self):
        return self.name_data
    
    def getFrameData(self):
        return self.frame_data
    
    # setters
    def setTotalSize(self, size): 
        self.total_size = size

    def buildPacket(self):
        name_bytes = self.name_data.encode('utf-8')
        frame_bytes = self.frame_data.encode('utf-8')
        total_size = 4 + len(name_bytes) + 4 + len(frame_bytes)
        packet_data = (
            total_size.to_bytes(4, byteorder='big') +
            len(name_bytes).to_bytes(4, byteorder='big') +
            name_bytes +
            len(frame_bytes).to_bytes(4, byteorder='big') +
            frame_bytes
        )
        return packet_data

    def parsePacket(self, data):
        offset = 0
        name_size = int.from_bytes(data[offset:offset + 4], byteorder='big')
        offset += 4
        self.name_data = data[offset:offset + name_size].decode('utf-8')
        offset += name_size
        frame_size = int.from_bytes(data[offset:offset + 4], byteorder='big')
        offset += 4
        self.frame_data = data[offset:offset + frame_size].decode('utf-8')


#-----------------------------------------------------------------------------------------
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