import cv2
import pyzbar.pyzbar as pyzbar
import MySQLdb


class QR_DB_Module:
    def __init__(self):
        self.USER = ''
        self.PASSWORD = ''
        self.HOST = ''
        self.DB = ''
        self.CHARSET = ''
        self.my_db = MySQLdb.connect(
            user=self.USER,
            passwd=self.PASSWORD,
            host=self.HOST,
            db=self.DB,
            charset=self.CHARSET
        )
        self.cursor = self.my_db.cursor(MySQLdb.cursors.DictCursor)

    def gstreamer_pipeline(self, sensor_id=0, capture_width=1280, capture_height=720, display_width=1280,
                                 display_height=720, framerate=60, flip_method=0):
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

    def get_barcode_info(self):
        cap = cv2.VideoCapture(self.gstreamer_pipeline(sensor_id=1, flip_method=0), cv2.CAP_GSTREAMER)
        personal_number = None
        cnt = 0
        while not personal_number and cnt < 5000:
            _, img = cap.read()
            img = cv2.resize(img, None, fx=0.4, fy=0.4)
            cv2.imshow('img', img)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            decoded = pyzbar.decode(gray)

            for d in decoded:
                personal_number = d.data.decode("utf-8")
            cnt += 1

        return personal_number

    def update_reward(self, personal_number, recycle_reward):
        sql = "SELECT * FROM user_list WHERE user_number = %s" % personal_number
        sql2 = "UPDATE user_list SET rw = rw+%s WHERE user_number = %s" % (recycle_reward, personal_number)
        self.update(sql2)
        rw = self.select(sql)

        return rw

    def select(self, sql):
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result[0]['rw']

    def update(self, sql):
        self.cursor.execute(sql)
        self.my_db.commit()


if __name__ == '__main__':
    dm = QR_DB_Module()
    personal_number = dm.get_barcode_info()
    rw = dm.update_reward(personal_number, '3')

