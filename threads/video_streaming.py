import socket
import threading
import time

import cv2
import numpy as np


class VideoStreaming(threading.Thread):

    timeout = 60

    def __init__(self, ip, port):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ip, int(port)))
        self.sock.setblocking(False)
        self.id = port
        self.frame = {'time': 0, 'frame': None}
        self.is_frame_new = False
        self.stop = False
        self.last_data_time = time.time()
        self.fps = 0
        print('Creating video streaming thread with id {}'.format(self.id))

    def run(self):
        data = b''
        buffer_size = 65536
        start = time.time()

        while True:
            if self.stop or (time.time() - self.last_data_time) > self.timeout:
                print('Killing video streaming thread with id {}'.format(self.id))
                self.id = None
                self.sock.close()
                break
            try:
                data += self.sock.recv(buffer_size)
                self.last_data_time = time.time()
            except BlockingIOError:
                pass
            a = data.find(b'\xff\xd8')
            b = data.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = data[a:b + 2]
                vt = data[b + 2: b + 2 + 8]
                data = data[b + 2 + 8:]
                # decode frame and video time
                self.frame['time'] = np.fromstring(vt, dtype=np.float64)[0]
                self.frame['frame'] = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),
                                                   cv2.IMREAD_COLOR)
                if self.frame is not None:
                    self.is_frame_new = True
                self.fps = 1 / (time.time() - start)
                start = time.time()

    def get_frame(self):
        self.is_frame_new = False
        return self.frame

    def has_new_frame(self):
        return self.is_frame_new

    def get_id(self):
        return self.id

    def get_fps(self):
        return self.fps

    def kill(self):
        self.stop = True
