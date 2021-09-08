#-* coding:utf-8 -*-
import os.path
import sys
import threading
import wave

import pyaudio
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from PyQt5 import uic
import azure.cognitiveservices.speech as speechsdk

# gui 클래스
from stt_team3.train import TextClassification

# gui form 정의
form_class = uic.loadUiType("main.ui")[0]

# stdout을 gui로 리다이렉트
class StdoutRedirect(object):
    def __init__(self, *param):
        self.daemon = True
        self.sysstdout = sys.stdout
        self.redirectout = param[0]
        sys.stdout.write = self.write

    def __del__(self):
        sys.stdout = self.sysstdout

    def write(self, s):
        self.redirectout(s)

class TrainWindow(QWidget):
    def __init__(self):
        super(TrainWindow, self).__init__()
        self.resize(400, 300)
        layout = QVBoxLayout()

        # data path
        self.labelPath = QLabel('train & val data path')
        self.editPath = QTextEdit(os.path.abspath("./augmented"))
        layout.addWidget(self.labelPath)
        layout.addWidget(self.editPath)

        # train and val rate
        self.labelTrainRatio = QLabel('training ratio of data set')
        self.editTrainRatio = QTextEdit("0.8")
        layout.addWidget(self.labelTrainRatio)
        layout.addWidget(self.editTrainRatio)

        # lr
        self.labelLR = QLabel('learning rate')
        self.editLR = QTextEdit("4")
        layout.addWidget(self.labelLR)
        layout.addWidget(self.editLR)

        # epochs
        self.labelEpoch = QLabel('epochs')
        self.editEpoch = QTextEdit("100")
        layout.addWidget(self.labelEpoch)
        layout.addWidget(self.editEpoch)

        # Batch
        self.labelBatch = QLabel('Batch size')
        self.editBatch = QTextEdit("2")
        layout.addWidget(self.labelBatch)
        layout.addWidget(self.editBatch)

        # train start button
        self.trainStartButton = QPushButton('train start')
        layout.addWidget(self.trainStartButton)
        # 학습 중에 프로그램이 멈춘것처럼 보이니까, 스레드로 돌리고
        # 중간 결과 stdout을 리다이렉트 할 것
        self.trainStartButton.clicked.connect(self.trainClicked)

        # consol stdout view
        self.stdoutView = QTextBrowser()
        layout.addWidget(self.stdoutView)
        self.stdoutView.setReadOnly(True)

        # set layout
        self.setLayout(layout)

    def trainClicked(self):
        self.trainStartButton.setEnabled(False)
        # stdout을 gui로 리다이렉트 진행
        # stdout이 발생할 때 마다 실행시킬 함수 전달(update)
        stdout_thread = StdoutRedirect(self.update)
        threading.Thread(target=self.train).start()

    def update(self, msg):
        # stdout 메시지 발생시, 이 함수 호출됨
        # msg를 view에 추가하고
        self.stdoutView.insertPlainText(msg)
        # 스크롤바를 아래로 옮김
        self.stdoutView.verticalScrollBar().setValue(self.stdoutView.verticalScrollBar().maximum())
        self.stdoutView.update()

    def train(self):
        test = TextClassification(batch_size = int(self.editBatch.toPlainText()) , lr = float(self.editLR.toPlainText()),
                                  epochs = int(self.editEpoch.toPlainText()), train_ratio = float(self.editTrainRatio.toPlainText()))
        test.makeDatasetAndVoc(dataPath=self.editPath.toPlainText())
        test.train()
        self.trainStartButton.setEnabled(True)

class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        # title name
        self.setWindowTitle("Sound to Text 음성 식별")

        print("-" * 10)
        print("preprocessing.. making vocabulary set for predict...")
        self.classifier = TextClassification()
        # 사전 만들기 작업 필요(모델을 불러올 때, 학습 데이터셋에서 만들어진 사전 사이즈를 맞춰줘야함)
        # 이 부분을 따로 함수로 빼놨으므로, 클래스 생성 후 사전 만들기 함수 호출
        self.classifier.makeDatasetAndVoc(dataPath="./augmented")
        print("preprocess finished")
        print("-" * 10)

        # 음성 인식 상태
        self.isRecording = False
        self.frame = []

        # type 체크 상태
        self.isType = False

        # train window
        self.train_window = TrainWindow()
        self.showTrainWindowButton = self.findChild(QPushButton, "trainWindowButton")
        self.showTrainWindowButton.clicked.connect(self.train_window.show)

        # 로고
        self.logo = self.findChild(QLabel, 'logo')

        # 작업 경로(weight 파일 위치 입력)
        self.data_root = "./sample_0.941.pth"

        # 수동 데이터 저장 경로
        self.save_text = self.findChild(QTextEdit, 'saveTextPath')
        self.save_text.setEnabled(False)
        self.save_dir = "./"
        self.save_text.setText(os.path.abspath(self.save_dir))

        # 수동 데이터 저장 브라우저
        self.saveBrowseButton = self.findChild(QPushButton, 'saveBrowseButton')
        self.saveBrowseButton.setEnabled(False)
        self.saveBrowseButton.clicked.connect(self.saveBrowse)

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

        # predict 버튼
        self.predictButton = self.findChild(QPushButton, 'predictButton')
        self.predictButton.clicked.connect(self.predict)
        self.predictButton.setEnabled(False)

        # okButton
        self.okButton = self.findChild(QPushButton, 'okButton')
        self.okButton.clicked.connect(self.ok)

        # soundToTextView
        self.soundToTextView = self.findChild(QTextEdit, 'soundToTextView')
        self.soundToTextView.setText("set subscription key")

        # weigh path browse 버튼
        self.browseButton = self.findChild(QPushButton, 'browseButton')
        self.browseButton.clicked.connect(self.browse)

        # weight path label
        self.browseEdit = self.findChild(QTextEdit, 'browseEdit')
        self.browseEdit.setText(os.path.abspath(self.data_root))

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

        # 타이핑 체크 박스
        self.typingButton = self.findChild(QCheckBox, 'typing')
        self.typingButton.clicked.connect(self.type)

    # predict 버튼 액션
    def predict(self):
        # 모델 불러오기
        self.classifier.load_model(self.data_root)

        # 텍스트 가져오기
        text = self.soundToTextView.toPlainText()
        # 가져온 텍스트로 예측 후 텍스트 뷰에 전달
        _, predictedLabel = self.classifier.predict(text)
        self.soundToTextView.setText(text + "\n" + "예측 : %s" % predictedLabel)

    # saveBrowse 버튼 액션
    def saveBrowse(self):
        self.save_dir = QFileDialog.getExistingDirectory(self, "save text dir", "./")
        self.save_text.setText(self.save_dir)

    # type 버튼 액션
    def type(self):
        if self.typingButton.isChecked():
            self.isType = True
            self.saveBrowseButton.setEnabled(True)
            self.okButton.setEnabled(False)
            self.startButton.setEnabled(False)
            self.stopButton.setEnabled(False)
            self.predictButton.setEnabled(False)
            self.saveButton.setEnabled(True)
            self.soundToTextView.setEnabled(True)
            self.greetingRadioButton.setDisabled(False)
            self.apologizeRadioButton.setDisabled(False)
            self.thankRadioButton.setDisabled(False)
            self.emergencyRadioButton.setDisabled(False)
            self.weatherRadioButton.setDisabled(False)
        else:
            self.isType = False
            self.saveBrowseButton.setEnabled(False)
            self.okButton.setEnabled(True)
            self.saveButton.setEnabled(False)
            self.soundToTextView.setEnabled(False)
            self.greetingRadioButton.setDisabled(True)
            self.apologizeRadioButton.setDisabled(True)
            self.thankRadioButton.setDisabled(True)
            self.emergencyRadioButton.setDisabled(True)
            self.weatherRadioButton.setDisabled(True)

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
        self.soundToTextView.setText("Press start and speak")
        self.predictButton.setEnabled(False)
        self.startButton.setEnabled(True)
        self.greetingRadioButton.setDisabled(True)
        self.weatherRadioButton.setDisabled(True)
        self.thankRadioButton.setDisabled(True)
        self.apologizeRadioButton.setDisabled(True)
        self.emergencyRadioButton.setDisabled(True)

    # 녹음 thread
    def rec(self):
        # 초기화
        self.frame = []
        while self.isRecording:
            data = self.stream.read(self.CHUNK)
            self.frame.append(data)

    # start 버튼 액션
    def start(self):
        # 초기화
        self.results = []
        self.soundToTextView.setText("Speak now, press stop to recognize")
        self.subscriptionKeyEdit.setDisabled(True)
        self.browseButton.setEnabled(False)
        self.okButton.setEnabled(False)
        self.startButton.setEnabled(False)
        self.greetingRadioButton.setDisabled(True)
        self.weatherRadioButton.setDisabled(True)
        self.thankRadioButton.setDisabled(True)
        self.apologizeRadioButton.setDisabled(True)
        self.emergencyRadioButton.setDisabled(True)

        # 녹음을 위한 pyaudio 사용
        self.p = pyaudio.PyAudio()

        # 음질 관련 설정
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100

        self.stream = self.p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)
        # 녹음 스레드 시작
        self.isRecording = True
        self.stream.start_stream()
        rec_thread = threading.Thread(target=self.rec)
        rec_thread.start()
        self.stopButton.setEnabled(True)

    # stop 버튼 액션
    def stop(self, evt):
        # isRecording이 False가 되면 스레드로 돌아가고있는 녹음 중단
        self.isRecording = False

        # 녹음 임시 저장
        audioName = "temp.wav"
        wf = wave.open(audioName, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frame))
        wf.close()

        # 애저 stt 호출
        speech_config = speechsdk.SpeechConfig(subscription=self.subscriptionKeyEdit.text(),
                                               region="koreacentral",
                                               speech_recognition_language="ko-KR")
        audio_input = speechsdk.AudioConfig(filename=audioName)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

        result = speech_recognizer.recognize_once_async().get()

        # 에러 핸들링
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            self.soundToTextView.setText(result.text)
        elif result.reason == speechsdk.ResultReason.NoMatch:
            self.soundToTextView.setText("No speech could be recognized: {}".format(result.no_match_details))
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            self.soundToTextView.setText("Speech Recognition canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                self.soundToTextView.setText("Error details: {}".format(cancellation_details.error_details))

        # ui 활성화
        self.subscriptionKeyEdit.setDisabled(False)
        self.browseButton.setEnabled(True)
        self.okButton.setEnabled(True)
        self.startButton.setEnabled(True)
        self.predictButton.setEnabled(True)

    # browse 버튼 액션
    def browse(self):
        path = 'pt'
        filter = 'All pt(*.pt; *.pth);; PT(*.pt);;PTH(*.pth)'
        filename = QFileDialog.getOpenFileName(self, 'load pth', path, filter)
        self.data_root = str(filename).split("'")[1]
        self.browseEdit.setText(self.data_root)

    # save 버튼 액션
    def save(self):
        text = self.soundToTextView.toPlainText()
        # 1번부터, 파일명 체크후 중복시 +1번 인덱스 부여해서 데이터 생성
        index = 1
        path = os.path.abspath(self.save_dir)
        # 인덱스 5자리맞추기, 5자리 넘어갈일 없을듯
        fname = path + os.path.sep + os.path.basename(path) + "_" +  str(index).zfill(5) + ".txt"
        while os.path.isfile(fname):
            index +=1
            fname = path + os.path.sep + os.path.basename(path) + "_" + str(index).zfill(5) + ".txt"

        f = open(fname, 'w', encoding='UTF-8')
        if self.greetingRadioButton.isChecked():
            label = '0'
        elif self.apologizeRadioButton.isChecked():
            label = '1'
        elif self.thankRadioButton.isChecked():
            label = '2'
        elif self.emergencyRadioButton.isChecked():
            label = '3'
        # self.weatherRadioButton.isChecked:
        else:
            label = '4'
        f.write(label + '\n')
        f.write(text)
        return
        f.close()

if __name__ == "__main__" :

    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()