# Object detection service

The detector is [A PyTorch implementation of a YOLO v3 Object Detector](https://github.com/ayooshkathuria/pytorch-yolo-v3). This service receives real time video, detects objects and prints the results.

## Setup
From `object-detection/`, do:
1. Install OpenCV library `$ sudo apt-get install libopencv-dev python-opencv`
2. Install Nvidia CUDA-9.0, following this [tutorial](https://yangcha.github.io/CUDA90/)
3. Create virtualenv `$ virtualenv --system-site-packages -p python3 venv`
4. Activate virtualenv `$ source venv/bin/activate`
5. Install requirements `$ pip install -r requirements.txt`
6. Download YOLO pre-trained weight file `$ wget https://pjreddie.com/media/files/yolov3.weights -P weights/`

## Testing
### Testing the module
There is a simple script to test if the detector module is working, to verify that the environment has been correctly configured. Run `$ python3 test/detector_test.py --image /path/to/image`. You should see a list with all the detected objects.

## Usage
 - Clone [python-live-video-streaming](https://github.com/jhonata-antunes/python-live-video-streaming) repo. It contains the video streaming client
 - Run the service `$ python3 service/manage.py runserver`
 - Inscribe a new video transmission `$ curl --data "port=5005" http://127.0.0.1:8000/object-detection/register/`, passing the port where the video is being transmitted to (after 120s without receiving video, you must register again)
 - To debug, receiving the video with detected objects run `curl --data "port=5005&debug_ip=localhost" http://127.0.0.1:8000/object-detection/register/` and, `python3 server.py` on your machine
 - Start video streaming `$ python3 client.py --video /path/to/video/file --port 5005`
 - If you don not want to process video any more, unsubscribe `$ curl --data "port=5005" http://127.0.0.1:8000/object-detection/unsubscribe/`
 - Get service status `$ curl http://127.0.0.1:8000/object-detection/status/
