import socket
import struct
import cv2
import numpy as np

#####################################
from qr_db_module import QR_DB_Module
from button_module import Button_Module
from motor_module import Motor_Module
#####################################


def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1280,
    capture_height=720,
    display_width=1280,
    display_height=720,
    framerate=60,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


cap = cv2.VideoCapture(gstreamer_pipeline(sensor_id=0, flip_method=0), cv2.CAP_GSTREAMER)

IP = '192.168.1.164'
PORT = 9484


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))

received_num = b''
reward = 0
is_button_clicked = True
QD = QR_DB_Module()
MM = Motor_Module(26, 24, 32, 33)

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
    received_num = s.recv(10)
    received_num = int(struct.unpack('f', received_num)[0])

    if received_num != -1:
        cur_reward = int(received_num % 1000)
        cur_object = classes[int(received_num/1000)]
        string = cur_object.split(' ')
        if string[0] == 'PET' and string[-1] == 'without_label':
            MM.move_two_motors(2, 10)
        elif string[0] == 'PAPER' and string[-1] == 'without_sticker' or 'without_cap':
            MM.move_two_motors(2, 12)
        elif string[0] == 'CAN':
            MM.move_two_motors(5, 12)
        MM.move_one_motor()
        MM.move_two_motors(2, 12)
        reward += cur_reward
        
    if is_button_clicked and reward > 0:
        personal_number = QD.get_barcode_info()
        if personal_number:
            QD.update_reward(personal_number, str(reward))
        is_button_clicked = False
        reward = 0

