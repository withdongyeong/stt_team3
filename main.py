#-* coding:utf-8 -*-
import os.path
import random
import sys
import time

import torch
from konlpy.tag import Komoran
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtCore, QtGui, QtWidgets
import azure.cognitiveservices.speech as speechsdk
from torch.utils.data import random_split
from torchtext.vocab import build_vocab_from_iterator

import customDataset
import nlpModel

print(sys.getdefaultencoding())

# gui 클래스
form_class = uic.loadUiType("main.ui")[0]
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        # 음성 인식 상태
        self.done = False
        self.results = []

        # type 체크 상태
        self.isType = False

        # 작업 경로(데이터 저장 위치)
        self.data_root = "."

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

        # 작업 경로 browse 버튼
        self.browseButton = self.findChild(QPushButton, 'browseButton')
        self.browseButton.clicked.connect(self.browse)

        # 작업 경로 label
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
        # 시드 고정

        SEED = 5
        # 랜덤함수 시드
        random.seed(SEED)
        # 토치 시드
        torch.manual_seed(SEED)

        # 데이터셋 만들기
        dataPath = "./conversationSet"
        dataset = customDataset.textDataset(dataPath)

        # random_split 함수를 통해 dataset을 비율을 맞춰 2개의 Subset으로 분리함
        num_train = int(len(dataset) * 0.8)
        train_dataset, test_dataset = \
            random_split(dataset, [num_train, len(dataset) - num_train])

        text = self.soundToTextView.toPlainText()
        print(text)
        komoran = Komoran()

        def yield_token(data_iter):
            for _, text in data_iter:
                yield komoran.morphs(text)

        # 어휘집 정의
        vocab = build_vocab_from_iterator(yield_token(train_dataset), specials=["<unk>"])
        vocab.set_default_index(vocab["<unk>"])

        text_pipeline = lambda x: vocab(komoran.morphs(x))

        n_classes = 5
        vocab_size = 254 # 이거 trainset 기반 숫자 맞춰야함, 따라서 클래스화 시킨 후 값 저장하고 호출해야함
        embeding_size = 64
        DEVICE = 'cpu'
        # 모델 선언
        model = nlpModel.TextClassificationModel(vocab_size, embeding_size, n_classes).to(DEVICE)
        model.load_state_dict(torch.load("./sample_0.893.pth"))
        model.eval()
        ag_news_label = {
            0: "인사",
            1: "감사",
            2: "사과",
            3: "위급",
            4: "날씨"
        }

        def predict(text, text_pipeline):
            with torch.no_grad():
                # print(text_pipeline(text))
                text = torch.tensor(text_pipeline(text))
                output = model(text, torch.tensor([0]))
                print(output)
                return output.argmax(1).item()

        print("예측 : %s" % ag_news_label[predict(text, text_pipeline)])

    # type 버튼 액션
    def type(self):
        if self.typingButton.isChecked():
            self.isType = True
            self.saveButton.setEnabled(True)
            self.soundToTextView.setEnabled(True)
            self.greetingRadioButton.setDisabled(False)
            self.apologizeRadioButton.setDisabled(False)
            self.thankRadioButton.setDisabled(False)
            self.emergencyRadioButton.setDisabled(False)
            self.weatherRadioButton.setDisabled(False)
        else:
            self.isType = False
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
        self.predictButton.setEnabled(True)
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

        if text == "":
            self.soundToTextView.setText("Nothing recognized")
        else:
            self.soundToTextView.setText(text)


    # browse 버튼 액션
    def browse(self):
        self.data_root = QFileDialog.getExistingDirectory(self, 'Open Folder', './')
        self.browseEdit.setText(self.data_root)

    # save 버튼 액션
    def save(self):
        text = self.soundToTextView.toPlainText()
        # 1번부터, 파일명 체크후 중복시 +1번 인덱스 부여해서 데이터 생성
        index = 1
        path = os.path.abspath(self.data_root)
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
