import cv2
import pickle

Node_Port = 22222
Packet_size = 60000
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
        # Calcule o número de bytes necessários para preencher o pacote
        padding_size = Packet_size - (4 + len(name_bytes) + 4 + len(frame_bytes))
        packet_data = (
            len(name_bytes).to_bytes(4, byteorder='big') +
            name_bytes +
            len(frame_bytes).to_bytes(4, byteorder='big') +
            frame_bytes +
            b'\x00' * padding_size
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
        self.track_data = caminho
        self.frame_data = frame

    def buildTrackedPacket(self):
        track_bytes = self.track_data.encode('utf-8')
        frame_bytes = self.frame_data.encode('utf-8')
        # Calcule o número de bytes necessários para preencher o pacote
        padding_size = Packet_size - (4 + len(track_bytes) + 4 + len(frame_bytes))
        packet_data = (
            len(track_bytes).to_bytes(4, byteorder='big') +
            track_bytes +
            len(frame_bytes).to_bytes(4, byteorder='big') +
            frame_bytes +
            b'\x00' * padding_size
        )
        return packet_data
    
    def parseTrackedPacket(self, data):
        offset = 0
        track_size = int.from_bytes(data[offset:offset + 4], byteorder='big')
        offset += 4
        self.track_data = data[offset:offset + track_size].decode('utf-8')
        offset += track_size
        frame_size = int.from_bytes(data[offset:offset + 4], byteorder='big')
        offset += 4
        self.frame_data = data[offset:offset + frame_size].decode('utf-8')