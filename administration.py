# 0: "인사",1: "감사", 2: "사과",3: "위급", 4: "날씨"
import random
import string

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QFont, QKeySequence
from PyQt5.QtCore import Qt
import sys
import os
from chardet import detect

form_class = uic.loadUiType('administration.ui')[0]


class Administration(QMainWindow, form_class):
    def __init__(self):
        super(Administration, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Administration')

        self.greetingRadio = self.findChild(QRadioButton, 'greetingRadio')
        self.apologizeRadio = self.findChild(QRadioButton, 'apologizeRadio')
        self.thanksRadio = self.findChild(QRadioButton, 'thanksRadio')
        self.emergencyRadio = self.findChild(QRadioButton, 'emergencyRadio')
        self.weatherRadio = self.findChild(QRadioButton, 'weatherRadio')

        self.chkBtn = self.findChild(QPushButton, 'chkBtn')
        self.chkBtn.clicked.connect(self.check)

        self.setPathBtn = self.findChild(QPushButton, 'setPathBtn')
        self.setPathBtn.clicked.connect(self.setTextFilePath)

        self.makeTextBtn = self.findChild(QPushButton, 'makeTextBtn')
        self.makeTextBtn.clicked.connect(self.toTextEditorPage)

        self.messageShow = self.findChild(QTableWidget, 'messageShow')
        self.messageShow.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.showStateLabel = self.findChild(QLabel, 'showStateLabel')

        self.greeting_ment = {}
        self.apologize_ment = {}
        self.thanks_ment = {}
        self.emergency_ment = {}
        self.weather_ment = {}

        self.data_root = os.path.abspath('.')
        txt_file = [txt for txt in os.listdir(self.data_root) if txt[-3:] == 'txt' and txt[0] != 'r']

        for txt in txt_file:
            txt_path = os.path.join(self.data_root, txt)
            with open(txt_path, 'r', encoding=self.find_codec(txt_path)) as f:
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
            self.showStateLabel.setText(f"인사의 텍스트 갯수는 {len(self.greeting_ment)} 입니다")

            for index, (file_name, text) in enumerate(self.greeting_ment.items()):
                self.messageShow.setItem(index, 0, QTableWidgetItem(file_name))
                self.messageShow.setItem(index, 1, QTableWidgetItem(text))

        elif self.apologizeRadio.isChecked():
            print('sorry')
            self.messageShow.setRowCount(len(self.apologize_ment))
            self.showStateLabel.setText(f"사과의 텍스트 갯수는 {len(self.apologize_ment)} 입니다")

            for index, (file_name, text) in enumerate(self.apologize_ment.items()):
                self.messageShow.setItem(index, 0, QTableWidgetItem(file_name))
                self.messageShow.setItem(index, 1, QTableWidgetItem(text))

        elif self.thanksRadio.isChecked():
            print('thanks')

            self.messageShow.setRowCount(len(self.thanks_ment))
            self.showStateLabel.setText(f"감사의 텍스트 갯수는 {len(self.thanks_ment)} 입니다")

            for index, (file_name, text) in enumerate(self.thanks_ment.items()):
                self.messageShow.setItem(index, 0, QTableWidgetItem(file_name))
                self.messageShow.setItem(index, 1, QTableWidgetItem(text))

        elif self.emergencyRadio.isChecked():
            print('help!!')

            self.messageShow.setRowCount(len(self.emergency_ment))
            self.showStateLabel.setText(f"위급의 텍스트 갯수는 {len(self.emergency_ment)} 입니다")

            for index, (file_name, text) in enumerate(self.emergency_ment.items()):
                self.messageShow.setItem(index, 0, QTableWidgetItem(file_name))
                self.messageShow.setItem(index, 1, QTableWidgetItem(text))

        elif self.weatherRadio.isChecked():
            print('how is the weather?')

            self.messageShow.setRowCount(len(self.weather_ment))
            self.showStateLabel.setText(f"날씨의 텍스트 갯수는 {len(self.weather_ment)} 입니다")

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

    def setTextFilePath(self):
        print('set text file path')
        self.greeting_ment.clear()
        self.apologize_ment.clear()
        self.thanks_ment.clear()
        self.emergency_ment.clear()
        self.weather_ment.clear()

        self.data_root = QFileDialog.getExistingDirectory(self, 'Open Folder', './')
        print(self.data_root)

        try:
            txt_file = [txt for txt in os.listdir(self.data_root) if txt[-3:] == 'txt']
        except FileNotFoundError:
            QMessageBox.information(self, '파일 경로 에러',
                                    '파일 경로 에러입니다.\n폴더를 txt파일만 있는 폴더를 지정해 주세요', QMessageBox.Yes)
            return

        for txt in txt_file:
            txt_path = os.path.join(self.data_root, txt)
            with open(txt_path, 'r', encoding=self.find_codec(txt_path)) as f:
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

    def toTextEditorPage(self):
        print('to text editor')
        self.hide()
        text_editor = TextEditor(self.data_root)
        text_editor.exec_()
        self.show()


form_text_editor = uic.loadUiType('textEditor.ui')[0]


class TextEditor(QDialog, QWidget, form_text_editor):

    def __init__(self, path):
        super(TextEditor, self).__init__()
        self.setupUi(self)
        self.save_path = path

        self.show()

        self.setPathBtn = self.findChild(QPushButton, 'setPathBtn')
        self.setPathBtn.clicked.connect(self.setSavePath)

        self.pathShowLabel = self.findChild(QLabel, 'pathShowLabel')
        self.pathShowLabel.setText(self.save_path)

        self.greetingRadio = self.findChild(QRadioButton, 'greetingRadio')
        self.apologizeRadio = self.findChild(QRadioButton, 'apologizeRadio')
        self.thanksRadio = self.findChild(QRadioButton, 'thanksRadio')
        self.emergencyRadio = self.findChild(QRadioButton, 'emergencyRadio')
        self.weatherRadio = self.findChild(QRadioButton, 'weatherRadio')

        self.textEditor = self.findChild(QPlainTextEdit, 'textEditor')
        self.textEditor.setFont(QFont('Ariel', 13))
        self.textEditor.setPlaceholderText('라벨 표시인 숫자 입력 대신에 편하게 글만 쓰고 저장하세요\n'
                                           '라벨링 처리를 알아서 해 줍니다\n'
                                           '그러면 위의 경로로 랜덤한 파일이름으로 저장됩니다.\n'
                                           '또한 단축키 ctrl + s를 누르면 자동으로 저장됩니다.')

        self.saveBtn = self.findChild(QPushButton, 'saveBtn')
        self.saveBtn.clicked.connect(self.save)

        self.cancleBtn = self.findChild(QPushButton, 'cancleBtn')
        self.cancleBtn.clicked.connect(self.cancle)


        self.shortCut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_S), self)
        self.shortCut.activated.connect(self.save)

    def setSavePath(self):
        print('path is changed')
        self.save_path = QFileDialog.getExistingDirectory(self, 'Open Folder', self.save_path)
        self.pathShowLabel.setText(self.save_path)

    def save(self):
        print('this file is saved')
        input_text = self.textEditor.toPlainText()
        input_text = input_text.strip()

        if len(input_text) == 0:
            QMessageBox.information(self, '내용 없음',
                                    '내용이 없습니다. 쓰시고 저장해 주세요', QMessageBox.Yes)
            return

        # 0: "인사",1: "감사", 2: "사과",3: "위급", 4: "날씨"

        if self.greetingRadio.isChecked():
            input_text = str(0) + '\n' + input_text
        elif self.thanksRadio.isChecked():
            input_text = str(1) + '\n' + input_text
        elif self.apologizeRadio.isChecked():
            input_text = str(2) + '\n' + input_text
        elif self.emergencyRadio.isChecked():
            input_text = str(3) + '\n' + input_text
        elif self.weatherRadio.isChecked():
            input_text = str(4) + '\n' + input_text
        elif not self.greetingRadio.isChecked() and not self.apologizeRadio.isChecked() and\
            not self.emergencyRadio.isChecked() and not self.weatherRadio.isChecked():
            QMessageBox.information(self, '라벨 에러',
                                    '라벨 에러입니다.\n라디오버튼의 라벨을 누르세요', QMessageBox.Yes)
            return
        else:
            print('Denied')

        print(input_text)

        #겹치는 일은 없겠지...?
        fname = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase, k=8)) + '.txt'
        save_path = os.path.join(self.save_path, fname)
        print(save_path)

        f = open(save_path, 'w', encoding='UTF-8')
        f.write(input_text)
        f.close()
        self.textEditor.clear()


    def cancle(self):
        print('cancle')
        self.textEditor.clear()
        self.close()

if __name__ == '__main__':
    # QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    # WindowClass의 인스턴스 생성
    myWindow = Administration()

    # 프로그램 화면을 보여주는 코드
    myWindow.show()

    # 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
