import paho.mqtt.client as mqtt


client_ip = "localhost"
broker_ip = "localhost"
object_detector_threads = {}

mqtt_client = mqtt.Client()
mqtt_client.connect(broker_ip)
mqtt_client.loop_start()
