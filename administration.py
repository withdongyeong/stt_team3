
# 0: "인사",1: "감사", 2: "사과",3: "위급", 4: "날씨"

from PyQt5.QtWidgets import *
from PyQt5 import uic
import sys
import os
from chardet import detect

form_class = uic.loadUiType('administration.ui')[0]

class Administration(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.greetingRadio = self.findChild(QRadioButton,'greetingRadio')
        self.apologizeRadio = self.findChild(QRadioButton, 'apologizeRadio')
        self.thanksRadio = self.findChild(QRadioButton, 'thanksRadio')
        self.emergencyRadio = self.findChild(QRadioButton, 'emergencyRadio')
        self.weatherRadio = self.findChild(QRadioButton, 'weatherRadio')

        self.chkBtn = self.findChild(QPushButton, 'chkBtn')
        self.chkBtn.clicked.connect(self.check)

        self.messageShow = self.findChild(QTableWidget, 'messageShow')
        self.messageShow.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.greeting_ment = {}
        self.apologize_ment = {}
        self.thanks_ment = {}
        self.emergency_ment = {}
        self.weather_ment = {}

        present_path = os.path.abspath('.')
        txt_file = [txt for txt in os.listdir(present_path) if txt[-3:] == 'txt' and txt[0] != 'r']

        for txt in txt_file:
            txt_path = os.path.join(present_path, txt)
            with open(txt_path, 'r', encoding = self.find_codec(txt_path)) as f:
                label = f.readline()
                text = f.readline()
                label = int(label.strip())
                text = text.strip()
                # print(text)
                # print(label)

                # 0: "인사",1: "감사", 2: "사과",3: "위급", 4: "날씨"
                if label == 0:
                    self.greeting_ment[txt] = text
                elif label == 1:
                    self.thanks_ment[txt] = text
                elif label == 2:
                    self.apologize_ment[txt] = text
                elif label == 3:
                    self.emergency_ment[txt] = text
                elif label == 4:
                    self.weather_ment[txt] = text
                else:
                    print('something is wrong')



    def check(self):


        self.messageShow.setColumnCount(2)

        if self.greetingRadio.isChecked():
            print('greeting')
            self.messageShow.setRowCount(len(self.greeting_ment))

            for index, (file_name, text) in enumerate(self.greeting_ment.items()):
                self.messageShow.setItem(index, 0, QTableWidgetItem(file_name))
                self.messageShow.setItem(index, 1, QTableWidgetItem(text))

        elif self.apologizeRadio.isChecked():
            print('sorry')
            self.messageShow.setRowCount(len(self.apologize_ment))

            for index, (file_name, text) in enumerate(self.apologize_ment.items()):
                self.messageShow.setItem(index, 0, QTableWidgetItem(file_name))
                self.messageShow.setItem(index, 1, QTableWidgetItem(text))

        elif self.thanksRadio.isChecked():
            print('thanks')

            self.messageShow.setRowCount(len(self.thanks_ment))

            for index, (file_name, text) in enumerate(self.thanks_ment.items()):
                self.messageShow.setItem(index, 0, QTableWidgetItem(file_name))
                self.messageShow.setItem(index, 1, QTableWidgetItem(text))

        elif self.emergencyRadio.isChecked():
            print('help!!')

            self.messageShow.setRowCount(len(self.emergency_ment))

            for index, (file_name, text) in enumerate(self.emergency_ment.items()):
                self.messageShow.setItem(index, 0, QTableWidgetItem(file_name))
                self.messageShow.setItem(index, 1, QTableWidgetItem(text))

        elif self.weatherRadio.isChecked():
            print('how is the weather?')

            self.messageShow.setRowCount(len(self.weather_ment))

            for index, (file_name, text) in enumerate(self.weather_ment.items()):
                self.messageShow.setItem(index, 0, QTableWidgetItem(file_name))
                self.messageShow.setItem(index, 1, QTableWidgetItem(text))

        self.messageShow.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


    def find_codec(self, file_path):

        '''텍스트 마다 인코딩이 다를 수 있으므로 인코딩을 찾아서 읽게 해 주는 함수'''

        # present_path = os.path.join(os.getcwd(), 'stt_team3')
        # print(file_path)

        # with open(os.path.join(present_path, file_path), 'rb') as file:
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            charset = detect(raw_data)['encoding']
            return charset
        return None

if __name__ == '__main__':
    # QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    # WindowClass의 인스턴스 생성
    myWindow = Administration()

    # 프로그램 화면을 보여주는 코드
    myWindow.show()

    # 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()