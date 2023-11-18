FRAME_WIDTH = 640
FRAME_HEIGHT = 480
Node_Port = 22222
Packet_size = 60000 

class Packet:
    def __init__(self, name, n, Frame):
        self.info = name
        self.frameNumber = n
        self.frame = Frame

    # getters
    def getInfo(self):
        return self.info
    
    def getFrameNumber(self):
        return self.frameNumber
    
    def getFrame(self):
        return self.frame

    def buildPacket(self):
        info_bytes = self.info.encode('utf-8')
        frame_bytes = self.frame

        # Calcule o número de bytes necessários para preencher o pacote
        padding_size = Packet_size - (4 + len(info_bytes) + 4 + len(frame_bytes))
        packet_data = (
            len(info_bytes).to_bytes(4, byteorder='big') +
            info_bytes +
            self.frameNumber.to_bytes(4, byteorder='big') +
            len(frame_bytes).to_bytes(4, byteorder='big') +
            frame_bytes +
            b'\x00' * padding_size
        )
        return packet_data

    def parsePacket(self, data):
        offset = 0
        name_size = int.from_bytes(data[offset:offset + 4], byteorder='big')
        offset += 4
        self.info = data[offset:offset + name_size].decode('utf-8')
        offset += name_size
        self.frameNumber = int.from_bytes(data[offset:offset + 4], byteorder='big')
        offset += 4
        frame_size = int.from_bytes(data[offset:offset + 4], byteorder='big')
        offset += 4
        self.frame = data[offset:offset + frame_size]