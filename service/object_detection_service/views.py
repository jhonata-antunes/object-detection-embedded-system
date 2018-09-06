import json
import os
import sys

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

sys.path.append('{}/../../'.format(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('{}/../'.format(os.path.dirname(os.path.abspath(__file__))))

from detector import Detector
from object_detection_service.models import client_ip, mqtt_client, object_detector_threads
from threads.object_detector import ObjectDetector
from threads.video_streaming import VideoStreaming


def messenger(message):
    mqtt_client.publish(topic="object-detection/objects", payload=json.dumps(message))


def on_detection_finish(od_id):
    del object_detector_threads[od_id]
    mqtt_client.publish(topic="object-detection/remove", payload=od_id)


@csrf_exempt
def register(request):
    if request.method == 'POST':
        debug_ip = request.POST.get('debug_ip')
        port = request.POST.get('port')
        try:
            int(port)
        except ValueError:
            return HttpResponse("Value {} can't be converted to integer".format(port),
                                status=400)
        if object_detector_threads.get(port) is not None:
            return HttpResponse("Port {} is already in use".format(port), status=400)
        detector = Detector()
        detector.load_model()
        vs = VideoStreaming(client_ip, port)
        od = ObjectDetector(vs, detector, messenger, on_detection_finish, debug_ip)
        od.start()
        object_detector_threads[port] = od
        mqtt_client.publish(topic="object-detection/add", payload=port)
        return HttpResponse("OK", status=200)
    else:
        return HttpResponse("Method not allowed", status=405)


@csrf_exempt
def unsubscribe(request):
    if request.method == 'POST':
        od_id = request.POST.get('port')
        object_detector = object_detector_threads.get(od_id)
        if object_detector is None:
            return HttpResponse("Port {} not found".format(od_id), status=404)
        else:
            object_detector.kill()
            return HttpResponse("OK", status=200)
    else:
        return HttpResponse("Method not allowed", status=405)


@csrf_exempt
def status(request):
    if request.method == 'GET':
        response = []
        for id_id, od in object_detector_threads.items():
            response.append({
                'id': od.get_id(),
                'video_fps': od.get_video_fps(),
                'detection_fps': od.get_detection_fps(),
            })
        return JsonResponse(response, safe=False)
    else:
        return HttpResponse("Method not allowed", status=405)
