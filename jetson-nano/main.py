import socket
import struct
import cv2
import numpy as np

#####################################
from qr_db_module import QR_DB_Module
from button_modul import Button_Module
#####################################


def gstreamer_pipeline(
    capture_width=1280,
    capture_height=720,
    display_width=1280,
    display_height=720,
    framerate=60,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)

IP = ''
PORT = 1234


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))

receieved_num = b''
reward = 0
is_button_clicked = False
QD = QR_DB_Module()
classes = {1: 'PET plastic_bottle with_label', 2: 'PET plastic_bottle without_label', 3: 'PAPER cardboard with_sticker',
            4: 'PAPER cardboard without_sticker', 5: 'PAPER coffee_cup with_cap', 6: 'PAPER coffee_cup without_cap',
            7: 'PAPER snack_box', 8: 'CAN drink_can'}


while True:
    _, img = cap.read()
    img = cv2.resize(img, None, fx=0.4, fy=0.4)
    result, frame = cv2.imencode('.jpg', img)
    data = np.array(frame)
    stringData = data.tostring()
    cur_object = None
    
    s.sendall((str(len(stringData))).encode().ljust(16) + stringData)
    receieved_num = s.recv(10)
    receieved_num = int(struct.unpack('f', receieved_num)[0])


    if receieved_num != -1:
        cur_reward = int(receieved_num % 1000)
        cur_object = classes[int(receieved_num/1000)]
        string = cur_object.split(' ')
        if string[0] == 'PET':
            if string[-1] == 'with_label':
                pass
        elif string[0] == 'PAPER':
            if string[-1] == 'with_sticker' or 'with_cap':
                pass
        elif string[0] == 'CAN':
            pass
        reward += cur_reward
        
    if is_button_clicked:
        personal_number = QD.get_barcode_info()
        QD.update_reward(personal_number, str(reward))
        is_button_clicked = False
        reward = 0
   
