# Welcome to PyShine
# lets make the client code
# Welcome to PyShine
# www.pyshine.com
import socket,cv2, pickle,struct

def main():
    host_ip = "127.0.0.1"   
    porta = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_address = (host_ip, porta)
    server_socket.bind(socket_address)
    server_socket.listen()
    print("RP à espera de conexão de servidores: ", socket_address)

    #client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #client_address = (host_ip, porta)
    #client_socket.connect(client_address)
    #print("Cliente connectado ao Servidor: ", client_address)

    client_socket, client_address = server_socket.accept()   # Aceita a conexão do cliente
    print("Conexão aceite da", client_address)
    data = b""
    payload_size = struct.calcsize("Q")
    while True:
        while len(data) < payload_size:
            packet = client_socket.recv(4*1024) # 4K
            if not packet: break
            data+=packet
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q",packed_msg_size)[0]
		
        while len(data) < msg_size:
            data += client_socket.recv(4*1024)
            frame_data = data[:msg_size]
            data  = data[msg_size:]
            frame = pickle.loads(frame_data)
            cv2.imshow("RECEIVING VIDEO FROM CACHE SERVER",frame)
            key = cv2.waitKey(1) & 0xFF
            if key  == ord('q'):
                break
    client_socket.close()

if __name__ == "__main__":
    main()
 