import torch
from torch.autograd import Variable

from src.darknet import Darknet
from model.object import Object
from src.preprocess import letterbox_image
from src.util import write_results, load_classes


def prep_image(img, inp_dim):
    """
    Prepare image for inputting to the neural network.
    :param img: numpy frame
    :param inp_dim:
    :return: Returns a Variable
    """
    orig_im = img
    dim = orig_im.shape[1], orig_im.shape[0]
    img = (letterbox_image(orig_im, (inp_dim, inp_dim)))
    img_ = img[:, :, ::-1].transpose((2, 0, 1)).copy()
    img_ = torch.from_numpy(img_).float().div(255.0).unsqueeze(0)
    return img_, orig_im, dim


class Detector:
    _model = None
    _dataset = "pascal"
    _confidence = 0.5
    _nms_thresh = 0.4
    _cfg = "cfg/yolov3.cfg"
    _weights = "weights/yolov3.weights"
    _resolution = "416"
    _cuda = False
    _num_classes = 80
    _classes = None

    def set_dataset(self, dataset: str):
        """
        :param dataset: Dataset on which the network has been trained
        :return:
        """
        if type(dataset) is not str:
            raise TypeError("dataset must be a string!")
        self._dataset = dataset

    def set_confidence(self, confidence: float):
        """
        :param confidence: Object Confidence to filter predictions
        :return:
        """
        if type(confidence) is not float:
            raise TypeError("confidence must be a float!")
        self._confidence = confidence

    def set_nms_thresh(self, nms_thresh: float):
        """
        :param nms_thresh: NMS Threshold
        :return:
        """
        if type(nms_thresh) is not float:
            raise TypeError("mns_thresh must be a float!")
        self._nms_thresh = nms_thresh

    def set_cfg(self, cfg: str):
        """
        :param cfg: Path to config file
        :return:
        """
        if type(cfg) is not str:
            raise TypeError("cfg must be a string!")
        self._cfg = cfg

    def set_weights(self, weights: str):
        """
        :param weights: Path to weights file
        :return:
        """
        if type(weights) is not str:
            raise TypeError("weights must be a string!")
        self._weights = weights

    def set_resolution(self, resolution: str):
        """
        :param resolution: Input resolution of the network.
        Increase to increase accuracy. Decrease to increase speed.
        :return:
        """
        if type(resolution) is not str:
            raise TypeError("resolution must be a string!")
        self._resolution = resolution

    def load_model(self):
        """
        Load the model and set its parameters
        :return:
        """
        print("Loading network...")
        self._classes = load_classes('data/coco.names')
        self._cuda = torch.cuda.is_available()

        self._model = Darknet(self._cfg)
        self._model.load_weights(self._weights)

        self._model.net_info["height"] = self._resolution
        inp_dim = int(self._model.net_info["height"])
        assert inp_dim % 32 == 0
        assert inp_dim > 32

        if self._cuda:
            self._model.cuda()

        # self._model(get_test_input(inp_dim, CUDA), CUDA)
        self._model.eval()
        print("Network successfully loaded!")

    def _create_object(self, t):
        """
        Creates an object, that represents the detected object
        :param t: tensor
        :return: dict
        """
        x1, y1 = int(t[1]), int(t[2])
        x2, y2 = int(t[3]), int(t[4])
        cls = int(t[7])
        obj = Object()
        obj.x = x1
        obj.y = y1
        obj.x2 = x2
        obj.y2 = y2
        obj.width = x2 - x1
        obj.height = y2 - y1
        obj.score = float(t[6])
        obj.label = "{0}".format(self._classes[cls])
        return obj.__dict__()

    def is_ready(self):
        return self._model is not None

    def detect(self, frame):
        """
        Use yolov3 model to detect objects
        :param frame: numpy frame
        :return: list containing Object, that represents a detected object
        """
        if self._model is None:
            raise ValueError("'load_model()' must be called first!")

        inp_dim = int(self._model.net_info["height"])
        img, orig_img, dim = prep_image(frame, inp_dim)
        img_dim = torch.FloatTensor(dim).repeat(1, 2)

        if self._cuda:
            img_dim = img_dim.cuda()
            img = img.cuda()

        with torch.no_grad():
            # tensor object
            output = self._model(Variable(img), self._cuda)

        output = write_results(output, self._confidence, self._num_classes,
                               nms=True, nms_conf=self._nms_thresh)

        if type(output) == int:
            output = []
        else:
            im_dim = img_dim.repeat(output.size(0), 1)
            scaling_factor = torch.min(inp_dim / im_dim, 1)[0].view(-1, 1)

            output[:, [1, 3]] -= (inp_dim - scaling_factor * im_dim[:, 0].view(-1, 1)) / 2
            output[:, [2, 4]] -= (inp_dim - scaling_factor * im_dim[:, 1].view(-1, 1)) / 2

            output[:, 1:5] /= scaling_factor

            for i in range(output.shape[0]):
                output[i, [1, 3]] = torch.clamp(output[i, [1, 3]], 0.0, im_dim[i, 0])
                output[i, [2, 4]] = torch.clamp(output[i, [2, 4]], 0.0, im_dim[i, 1])

        object_list = []
        for obj in output:
            object_list.append(self._create_object(obj))

        return object_list
