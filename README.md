# Object detection service

The detector is [A PyTorch implementation of a YOLO v3 Object Detector](https://github.com/ayooshkathuria/pytorch-yolo-v3).

## Setup
From `object-detection/`, do:
1. Install OpenCV library `$ sudo apt-get install libopencv-dev python-opencv`
2. Create virtualenv `$ virtualenv --system-site-packages -p python3 venv`
3. Activate virtualenv `$ source venv/bin/activate`
4. Install requirements `$ pip install -r requirements.txt`
5. Download YOLO pre-trained weight file `$ wget https://pjreddie.com/media/files/yolov3-tiny.weights -P weights/`

## Testing
### Testing the module
There is a simple script to test if the detector module is working, to verify that the environment has been correctly configured. Run `$ python3 test/detector_test.py --image /path/to/image`. You should see a list with all the detected objects.

## Usage
 - Run `$ python3 main.py`, and check if the green led is turned on
   - `--video VIDEO` Path to video file (default value: Camera)
   - `--gray` Convert video into gray scale before apply detection (default value: `None`)
