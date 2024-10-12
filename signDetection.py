import cv2
from openvino.inference_engine import IECore

USE_CAMERA = False

videoPath = ""

if USE_CAMERA:
    videoSource = cv2.VideoCapture(0)
else:
    videoSource = cv2.VideoCapture(videoPath)

while True:
    ret, frame = videoSource.read()

    if not ret:
        break

ie = IECore()
net = ie.read_network(model='model.xml', weights='model.bin')
exec_net = ie.load_