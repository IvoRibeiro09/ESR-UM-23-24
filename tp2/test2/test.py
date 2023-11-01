import cv2
import base64
import socket
import time
import numpy as np
import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk

class VideoStreaming:
    def __init__(self, client_socket, client_address, queue, FPS=30):
        self.client_socket = client_socket
        self.client_address = client_address
        self.queue = queue
        self.FPS = FPS
        self.TS = 1.0  # Initial timestamp
        self.start_streaming()

    def start_streaming(self):
        root = tk.Tk()
        root.title("Video Streaming")

        frame_label = tk.Label(root)
        frame_label.pack()

        fps, st, frames_to_count, cnt = (0, 0, 1, 0)
        WIDTH = 400

        while True:
            frame = self.queue.get()
            encoded, buffer = cv2.imencode('.jpeg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            message = base64.b64encode(buffer)
            self.client_socket.sendto(message, self.client_address)

            if cnt == frames_to_count:
                try:
                    fps = frames_to_count / (time.time() - st)
                    st = time.time()
                    cnt = 0
                    if fps > self.FPS:
                        self.TS += 0.001
                    elif fps < self.FPS:
                        self.TS -= 0.001
                    else:
                        pass
                except:
                    pass
            cnt += 1

            # Display the frame in a custom GUI window
            frame_data = base64.b64decode(message)
            nparr = np.frombuffer(frame_data, np.uint8)
            frame_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            frame_image = cv2.cvtColor(frame_image, cv2.COLOR_BGR2RGB)
            frame_image = Image.fromarray(frame_image)
            frame_image = ImageTk.PhotoImage(image=frame_image)

            frame_label.config(image=frame_image)
            frame_label.image = frame_image

            root.update_idletasks()
            root.update()

if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('0.0.0.0', 12345))

    queue = YourQueueImplementation()  # Replace with your queue implementation
    video_streaming = VideoStreaming(server_socket, ('client_ip', 12345), queue, FPS=30)
