import sys
import time

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
        # 음성 인식 상태
        self.done = False
        self.results = []

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
        # 초기화
        self.done = False
        self.results = []
        self.soundToTextView.setText("Speak now, press stop to recognize")
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
            self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config)
            # 콜백과 이벤트 연결
            # speech_recognizer가 각 상황에 맞춰 콜백을 보낼 건데, 그 콜백이 일어났을 때
            # 일어날 이벤트를 connect
            self.speech_recognizer.recognized.connect(self.save_result)
            self.speech_recognizer.session_stopped.connect(self.stop)
            self.speech_recognizer.canceled.connect(self.stop)
            # 식별 시작
            self.speech_recognizer.start_continuous_recognition()
        except:
            self.soundToTextView.setText("error occured, check mic is connected")
            return

    # 인식 결과 저장
    def save_result(self, evt):
        print(evt)
        self.results.append(evt.result)

    # stop 버튼 액션
    def stop(self, evt):
        # 이 부분이 없으면, stop이 2번 호출됨
        # 또한 stop 버튼 누르자마자 stop이 안됨
        # 누르자마자 stop하도록 고치고 싶음
        if self.done == True:
            return
        self.done = True

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

        self.speech_recognizer.stop_continuous_recognition()
        results = self.results
        text = ""
        # result에는 인식된 것만 들어가있을 것 같은데, 아닐 경우에 해당 idx 오류 출력
        # 인식된것만 text에 추가
        for i, result in enumerate(results):
            # 정상 인식
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                text += result.text + "\n"
            # 에러 케이스
            elif result.reason == speechsdk.ResultReason.NoMatch:
                print("No speech could be recognized {}: {}".format(i, result.no_match_details))
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print("Speech Recognition canceled {}: {}".format(i, cancellation_details.reason))
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    print("Error details {}: {}".format(i, cancellation_details.error_details))

        self.soundToTextView.setText(text)

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
