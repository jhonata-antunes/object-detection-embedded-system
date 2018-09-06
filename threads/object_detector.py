import numpy as np

import cv2
import socket
import threading
import time


class ObjectDetector(threading.Thread):

    def __init__(self, vs, detector, messenger, on_finish, debug_ip):
        super().__init__()
        self.vs = vs
        self.detector = detector
        self.messenger = messenger
        self.stop = False
        self.vs.start()
        self.id = vs.get_id()
        self.fps = 0
        self.callback = on_finish
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.debug_ip = debug_ip
        print('Creating object detector thread with id {}'.format(self.id))

    def run(self):
        start = time.time()

        while True:
            if self.stop or not self.vs.isAlive():
                self.vs.kill()
                print('Killing object detector thread with id {}'.format(self.id))
                self.callback(self.id)
                self.id = None
                break

            if self.vs.has_new_frame():
                frame = self.vs.get_frame()
                objects = self.detector.detect(frame['frame'])
                if self.debug_ip:
                    threading.Thread(target=self.send_detection, args=(frame['frame'], objects)).start()
                self.fps = 1 / (time.time() - start)
                start = time.time()
                self.messenger({'id': self.id, 'time': frame['time'], 'objects': objects})

    def kill(self):
        self.stop = True

    def get_id(self):
        return self.id

    def get_video_fps(self):
        return self.vs.get_fps()

    def get_detection_fps(self):
        return self.fps

    def send_detection(self, frame, objects):
        """
        Method to debug detection of person
        :return:
        """
        try:
            for obj in objects:
                if obj.get('label') == 'person':
                    frame = draw_box(frame, obj, (0, 255, 0))

            max_size = 65536 - 8  # less 8 bytes of video time
            jpg_quality = 80

            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), jpg_quality]
            result, encoded_img = cv2.imencode('.jpg', frame, encode_param)
            # Decrease quality until frame size is less than 65k
            while encoded_img.nbytes > max_size:
                jpg_quality -= 5
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), jpg_quality]
                result, encoded_img = cv2.imencode('.jpg', frame, encode_param)

            vt = np.array([0], dtype=np.float64)
            data = encoded_img.tobytes() + vt.tobytes()

            self.sock.sendto(data, (self.debug_ip, 5005))
        except Exception as ex:
            print(ex)


def draw_box(frame, obj, color_bgr, thickness=2):
    """
    Draw a rectangle in an numpy frame
    :param frame: numpy frame
    :param obj: dict with detected object
    :param color_bgr: color
    :param thickness: thickness of rectangle
    :return: numpy frame
    """
    top_left = (obj['x'], obj['y'])
    bottom_right = (obj['x'] + obj['width'], obj['y'] + obj['height'])
    return cv2.rectangle(frame, top_left, bottom_right, color_bgr, thickness)
