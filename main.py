import cv2
import json
import numpy as np
from playsound import playsound
from collections import defaultdict

##################################################
from yolo_module import Object_Detection
from display_module import Display_Module
##################################################


class Recycling:
    def __init__(self):
        with open("./recycle_information.json", 'r', encoding='UTF-8') as file:
            self.info = json.load(file)
        self.classes = {0: 'PET plastic_bottle with_label', 1: 'PET plastic_bottle without_label', 2: 'PAPER cardboard with_sticker',
                        3: 'PAPER cardboard without_sticker', 4: 'PAPER coffee_cup with_cap', 5: 'PAPER coffee_cup without_cap',
                        6: 'PAPER snack_box', 7: 'CAN drink_can'}
        self.object_cnt = defaultdict(int)
        self.path = "./audio/"
        self.is_button_clicked = False
        self.reward = 0
        self.DM = Display_Module()
        self.OD = Object_Detection()

    def start_capturing(self):
        cap = cv2.VideoCapture(0)
        while True:
            _, img = cap.read()
            img = cv2.resize(img, None, fx=0.4, fy=0.4)
            modified_img = self.get_info(img)
            cv2.imshow('img', modified_img)
            cv2.waitKey(1)

    def get_info(self, img):
        changed_img, object_x, object_y, object_w, object_h, class_id = self.OD.detect_object(img)
        if class_id != -1 and (object_x != -1 or object_y != -1 or object_w != -1 or object_h != -1):
            detected_object = self.classes[class_id]
            cv2.putText(changed_img, self.classes[class_id], (object_x - 10, object_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (0, 255, 0), 2)
            self.object_cnt[class_id] += 1
            idx = max(self.object_cnt, key=lambda key: self.object_cnt[key])
            if self.object_cnt[idx] > 30:
                string = detected_object.split(' ')
                playsound(self.path + string[1] + ' ' + string[2] + '.mp3')
                self.reward += int(self.info[string[0]][string[1]][1])
                self.object_cnt.clear()
            if self.is_button_clicked:
                personal_number = self.DM.get_barcode_info()
                self.DM.update_reward(personal_number, str(self.reward))
                self.is_button_clicked = False
                self.reward = 0
            return changed_img

        return img


if __name__ == '__main__':
    recycle = Recycling()
    recycle.start_capturing()

