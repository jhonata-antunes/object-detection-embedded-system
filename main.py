import argparse
import time

import cv2

from detector import Detector


def arg_parse():
    parser = argparse.ArgumentParser(description='Main')
    parser.add_argument("--video", help="Path to video file", default=0)
    parser.add_argument("--gray", help="Convert video into gray scale before apply detection", action="store_true")

    return parser.parse_args()


def green_led(on):
    if on:
        # TODO: turn on
        pass
    else:
        # TODO: turn off
        pass


def main(args):
    detector = Detector()
    detector.load_model()
    cap = cv2.VideoCapture(args.video)

    start = time.time()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if args.gray:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        objects = detector.detect(frame)
        objects = [obj for obj in objects if obj['label'] == 'person']

        if len(objects) > 0:
            green_led(on=True)
        else:
            green_led(on=False)

        end = time.time()
        print('FPS: {0:0.2f}'.format(1 / (end - start)))
        start = time.time()


if __name__ == '__main__':
    arguments = arg_parse()
    main(arguments)
