import cv2
import numpy as np


class Object_Detection:
    def __init__(self):
        self.net = cv2.dnn.readNet("./yolo_file/yolov3-tiny_obj_best.weights", "./yolo_file/yolov3-tiny_obj.cfg")
        self.layer_names = self.net.getLayerNames()
        self.output_layers = [self.layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

    def detect_object(self, img):
        x, y, w, h = -1, -1, -1, -1
        # img = cv2.resize(img, None, fx=0.4, fy=0.4)
        height, width, _ = img.shape
        class_id = -1

        blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

        self.net.setInput(blob)
        outs = self.net.forward(self.output_layers)

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.7:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    # x *= 10 / 4
                    # y *= 10 / 4
                    # h *= 10 / 4
                    # w *= 10 / 4
                    # img = cv2.resize(img, None, fx=10/4, fy=10/4)
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    return img, x, y, w, h, class_id

        return img, x, y, w, h, class_id
