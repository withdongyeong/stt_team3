import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtCore, QtGui, QtWidgets
import azure.cognitiveservices.speech as speechsdk

# gui 클래스
form_class = uic.loadUiType("main.ui")[0]
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        # 구독 key label
        self.subscriptionKeyLabel = self.findChild(QLabel, 'subscriptionKeyLabel')

        # 구독 key edit
        self.subscriptionKeyEdit = self.findChild(QLineEdit, 'subscriptionKeyEdit')

        # start 버튼
        self.startButton = self.findChild(QPushButton, 'startButton')
        self.startButton.clicked.connect(self.start)
        self.startButton.setEnabled(False)

        # stop 버튼
        self.stopButton = self.findChild(QPushButton, 'stopButton')
        self.stopButton.clicked.connect(self.stop)
        self.stopButton.setEnabled(False)

        # okButton
        self.okButton = self.findChild(QPushButton, 'okButton')
        self.okButton.clicked.connect(self.ok)

        # soundToTextView
        self.soundToTextView = self.findChild(QTextEdit, 'soundToTextView')
        self.soundToTextView.setText("set subscription key")

        # 작업 경로 browse 버튼
        self.browseButton = self.findChild(QPushButton, 'browseButton')
        self.browseButton.clicked.connect(self.browse)

        # 작업 경로 label
        self.browseLabel = self.findChild(QLabel, 'browseLabel')

        # 인사 라디오 버튼
        self.greetingRadioButton = self.findChild(QRadioButton, 'greetingRadioButton')
        self.greetingRadioButton.setChecked(True)
        self.greetingRadioButton.setDisabled(True)

        # 사과 라디오 버튼
        self.apologizeRadioButton = self.findChild(QRadioButton, 'apologizeRadioButton')
        self.apologizeRadioButton.setDisabled(True)

        # 감사 라디오 버튼
        self.thankRadioButton = self.findChild(QRadioButton, 'thankRadioButton')
        self.thankRadioButton.setDisabled(True)

        # 위급 라디오 버튼
        self.emergencyRadioButton = self.findChild(QRadioButton, 'emergencyRadioButton')
        self.emergencyRadioButton.setDisabled(True)

        # 날씨 라디오 버튼
        self.weatherRadioButton = self.findChild(QRadioButton, 'weatherRadioButton')
        self.weatherRadioButton.setDisabled(True)

        # 저장 버튼
        self.saveButton = self.findChild(QPushButton, 'saveButton')
        self.saveButton.clicked.connect(self.save)
        self.saveButton.setEnabled(False)

    # ok 버튼 액션
    def ok(self):
        # config azure stt
        try:
            self.speech_config = speechsdk.SpeechConfig(subscription=self.subscriptionKeyEdit.text(),
                                                   region="koreacentral",
                                                   speech_recognition_language="ko-KR")
        except:
            self.soundToTextView.setText("subscription key is wrong")
            return
        self.soundToTextView.setText("press start and speak")
        self.startButton.setEnabled(True)
        self.greetingRadioButton.setDisabled(True)
        self.weatherRadioButton.setDisabled(True)
        self.thankRadioButton.setDisabled(True)
        self.apologizeRadioButton.setDisabled(True)
        self.emergencyRadioButton.setDisabled(True)

    # start 버튼 액션
    def start(self):
        self.soundToTextView.setText("Speak now")
        self.subscriptionKeyEdit.setDisabled(True)
        self.browseButton.setEnabled(False)
        self.okButton.setEnabled(False)
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.greetingRadioButton.setDisabled(True)
        self.weatherRadioButton.setDisabled(True)
        self.thankRadioButton.setDisabled(True)
        self.apologizeRadioButton.setDisabled(True)
        self.emergencyRadioButton.setDisabled(True)
        try:
            speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config)
            result = speech_recognizer.recognize_once_async().get()
            # 정상 인식
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                self.soundToTextView.setText("Recognized: {}".format(result.text))
            # 에러 케이스
            elif result.reason == speechsdk.ResultReason.NoMatch:
                self.soundToTextView.setText("No speech could be recognized: {}".format(result.no_match_details))
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                self.soundToTextView.setText("Speech Recognition canceled: {}".format(cancellation_details.reason))
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    self.soundToTextView.setText("Error details: {}".format(cancellation_details.error_details))
        except:
            self.soundToTextView.setText("error occured, check mic is connected")
            return

    # stop 버튼 액션
    def stop(self):
        self.subscriptionKeyEdit.setDisabled(False)
        self.browseButton.setEnabled(True)
        self.okButton.setEnabled(True)
        self.startButton.setEnabled(True)
        self.greetingRadioButton.setDisabled(False)
        self.weatherRadioButton.setDisabled(False)
        self.thankRadioButton.setDisabled(False)
        self.apologizeRadioButton.setDisabled(False)
        self.emergencyRadioButton.setDisabled(False)
        self.saveButton.setEnabled(True)

    # browse 버튼 액션
    def browse(self):
        pass

    # save 버튼 액션
    def save(self):
        pass

if __name__ == "__main__" :

    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
