import cv2
import json
import threading
import numpy as np
from collections import defaultdict

##################################################
from yolo_module import Object_Detection
##################################################


class QR(threading.Thread):
    def __init__(self):
        super(QR, self).__init__()
        self._stop_event = threading.Event()
        self.is_running = True
        self.is_detected_qr = False
        self.flag = False
        self.QR = 1

    def stop(self):
        self._stop_event.set()

    def get_qr(self):
        self.QR = 'text'
        return self.QR, self.flag

    def run(self):
        while not self._stop_event.is_set():
            if self.is_running:
                if self.is_detected_qr:
                    self.is_running = False
                    self.flag = True
                    self.is_detected_qr = False


class Recycling:
    def __init__(self):
        with open("./recycle_information.json", 'r', encoding='UTF-8') as file:
            self.info = json.load(file)
        self.classes = {0: 'PET plastic_bottle with label', 1: 'PET plastic_bottle without label', 2: 'PAPER cardboard',
                        3: 'PAPER coffee_cup', 4: 'PAPER snack_box', 5: 'CAN drink_can'}
        self.object_cnt = defaultdict(int)
        self.OD = Object_Detection()
        self.qr = QR()
        self.qr.daemon = True

    def start_capturing(self):
        cap = cv2.VideoCapture(0)
        while True:
            _, img = cap.read()
            modified_img = self.draw_and_text(img)
            cv2.imshow('img', modified_img)
            cv2.waitKey(1)

    def draw_and_text(self, img):
        changed_img, object_x, object_y, object_w, object_h, class_id = self.OD.detect_object(img)
        if class_id != -1 and (object_x != -1 or object_y != -1 or object_w != -1 or object_h != -1):
            detected_object = self.classes[class_id]
            cv2.putText(changed_img, self.classes[class_id], (object_x - 10, object_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (0, 255, 0), 2)
            self.object_cnt[class_id] += 1
            idx = max(self.object_cnt, key=lambda key: self.object_cnt[key])
            if self.object_cnt[idx] > 50:
                string = detected_object.split(' ')
                print(self.info[string[0]][string[1]][0])
                print('Points : %d' % int(self.info[string[0]][string[1]][1]))
                self.object_cnt.clear()
            return changed_img
        return img

    def start_qr(self):
        self.qr.start()


if __name__ == '__main__':
    recycle = Recycling()
    recycle.start_capturing()

