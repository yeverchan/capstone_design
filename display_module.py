import cv2
import pyzbar.pyzbar as pyzbar
import pymysql


class Display_Module:
    def __init__(self):
        self.USER = ''
        self.PASSWORD = ''
        self.HOST = ''
        self.DB = ''
        self.CHARSET = 'utf8'
        self.my_db = pymysql.connect(
            user=self.USER,
            passwd=self.PASSWORD,
            host=self.HOST,
            db=self.DB,
            charset=self.CHARSET
        )
        self.cursor = self.my_db.cursor(pymysql.cursors.DictCursor)

    def get_barcode_info(self):
        cap = cv2.VideoCapture(0)
        personal_number = None
        while not personal_number:
            _, img = cap.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            decoded = pyzbar.decode(gray)

            for d in decoded:
                personal_number = d.data.decode("utf-8")

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
    dm = Display_Module()
    personal_number = dm.get_barcode_info()
    rw = dm.update_reward(personal_number, '3')

