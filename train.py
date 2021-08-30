import glob
import os
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchtext.legacy.data
from torch.utils.data import Subset, DataLoader, random_split
from torchtext import data, datasets
import random
from sklearn.model_selection import ShuffleSplit
from konlpy.tag import Okt, Komoran
from torchtext.vocab import build_vocab_from_iterator
import customDataset, nlpModel

# 하이퍼 파라미터 정의
# 하이퍼 파라미터
BATCH_SIZE = 2
lr = 4
EPOCHS = 1000

# train 함수 정의
def train(model, optimizer, dataloader, criterion):
    model.train()
    total_acc, total_count = 0, 0
    log_interval = 500
    start_time = time.time()
    for idx, (label, text, offsets) in enumerate(dataloader):
        optimizer.zero_grad()
        predicted_label = model(text, offsets)

        loss = criterion(predicted_label, label)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 0.1)
        optimizer.step()
        total_acc += (predicted_label.argmax(1) == label).sum().item()
        total_count += label.size(0)
        if idx % log_interval == 0 and idx > 0:
            elapsed = time.time() - start_time
            print('| epoch {:3d} | {:5d}/{:5d} batches '
                  '| accuracy {:8.3f}'.format(EPOCHS, idx, len(dataloader),
                                              total_acc / total_count))
            total_acc, total_count = 0, 0
            start_time = time.time()

# evaluate 함수 정의
def evaluate(dataloader):
    model.eval()
    total_acc, total_count = 0, 0

    with torch.no_grad():
        for idx, (label, text, offsets) in enumerate(dataloader):
            predited_label = model(text, offsets)
            loss = criterion(predited_label, label)
            total_acc += (predited_label.argmax(1) == label).sum().item()
            total_count += label.size(0)
    return total_acc/total_count


# 시드 고정

SEED = 5
# 랜덤함수 시드
random.seed(SEED)
# 토치 시드
torch.manual_seed(SEED)

# gpu 사용
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 데이터셋을 만들고, 학습 및 테스트 데이터셋으로 분리
# 데이터셋 만들기
dataPath = "./conversationSet"
dataset = customDataset.textDataset(dataPath)

# random_split 함수를 통해 dataset을 비율을 맞춰 2개의 Subset으로 분리함
num_train = int(len(dataset) * 0.8)
train_dataset, test_dataset = \
    random_split(dataset, [num_train, len(dataset) - num_train])

# NLP 텍스트 처리를 위해서는,
# 어휘집, 단어벡트, 토크나이저를 통하여 전처리를 해야한다
# 먼저,
# 형태소 분석기(토크나이저)는 KoNLPy를 통해
# Okt, Mecab, Komoran, Hannanum, Kkma 등을 사용할 수 있는데
# Mecab 이 속도가 빨라서 많이 사용된다고 하나, 설치법이 까다로워
# 일단 쉽게 사용할 수 있는 다른 형태소 분석기를 사용해본다

# https://iostream.tistory.com/144 에서 간단히 각 형태소 분석기 성능을 비교했고
# 각기 장단점이 있다

# 품질 적인 측면에서 Komoran을 선정하였다
# 사용가능한 명령은
# morphs(), pos(), nouns()가 있다
"""
konlpy를 사용하기 위해서는 (아나콘다 환경 기준)
1. jdk 설치 및 환경 변수 설정 ( 환경 변수 설정 후 cmd 창에서 java -version 입력 후 잘 설치되어있는지 확인)
2. Jpype1을 설치
3. konlpy를 설치
가 필요하다

1은 방법이 길어 검색을 통해 직접 해결해야하겠고,
2를 위해서는 자신의 python 버전, os에 맞춰(터미널에서 python --version으로 확인)
https://www.lfd.uci.edu/~gohlke/pythonlibs/#jpype
에서 .whl 파일을 다운로드해야한다 (pip install jpype1로 설치할 수 없다)

예를 들어 파이썬 버전이 3.8.8, window 64bit일 경우
JPype1‑1.3.0‑cp38‑cp38‑win_amd64.whl을 다운로드한다
그 후 pip install <다운로드한 파일 경로>를 통해 jpype1을 설치한다

버전 호환성 문제가 있는지 
SystemError: java.nio.file.InvalidPathException: Illegal char <*> ~~ 와 같은 오류가 발생한다
pip install jpype1==0.7.0 로 다운그레이드 하니 해결되었다
"""

#komoran 객체 생성
komoran = Komoran()

# iterable 객체를 전달받아서 토큰화 시키는 생성자
def yield_token(data_iter):
    for _, text in data_iter:
        yield komoran.nouns(text)

# 어휘집 정의
vocab = build_vocab_from_iterator(yield_token(train_dataset), specials=["<unk>"])
vocab.set_default_index(vocab["<unk>"])

# komoran에 의해 토큰화된 단어들이 어휘집에 들어가게 됨
# komoran의 식별률에 달려있는 부분
# 명사 식별률이 생각보다 낮은데, 최악의 경우엔 토크나이저를 쓰지 않고
# space 단위로 토큰화시켜야할듯함

# 텍스트처리 파이프라인은
# 데이터셋 반복자로부터 얻어온 가공되지 않은 문장 데이터를 처리할 떄 사용
# lambda 함수로 정의되어있어 text_pipeline(x) 와 같이 사용할 수 있음
text_pipeline = lambda x: vocab(komoran.morphs(x))
label_pipeline = lambda x: int(x)

# label 파이프라인은 label을 int label로 변환해줌
# collate_batch 함수는 dataLoader 선언시, collate_fn에 대입
# 각 배치에 대해 이 함수를 적용한다라고 생각하면 되며,
# 배치에서 뽑아낸 label 및 text를 tensor화 시켜묶어냄
# offset 은 텍스트 텐서에서 개별 시퀀스 시작 인덱스를 표현하기 위함
def collate_batch(batch):
    label_list, text_list, offsets = [], [], [0]
    for (_label, _text) in batch:
         label_list.append(label_pipeline(_label))
         processed_text = torch.tensor(text_pipeline(_text), dtype=torch.int64)
         text_list.append(processed_text)
         offsets.append(processed_text.size(0))
    label_list = torch.tensor(label_list, dtype=torch.int64)
    offsets = torch.tensor(offsets[:-1]).cumsum(dim=0)
    text_list = torch.cat(text_list)
    return label_list.to(DEVICE), text_list.to(DEVICE), offsets.to(DEVICE)

# data loader 정의
dataLoader_train = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=False,
                              collate_fn=collate_batch)
dataLoader_test = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False,
                              collate_fn=collate_batch)

n_classes = 5
vocab_size = len(vocab)
embeding_size = 64
# 모델 선언
model = nlpModel.TextClassificationModel(vocab_size, embeding_size, n_classes).to(DEVICE)
optimizer = torch.optim.SGD(model.parameters(), lr=lr)
criterion = torch.nn.CrossEntropyLoss()
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, 1.0, gamma=0.1)
total_accu = None

for epoch in range(1, EPOCHS + 1):
    epoch_start_time = time.time()
    train(model, optimizer, dataLoader_train, criterion)
    accu_val = evaluate(dataLoader_test)
    if total_accu is not None and total_accu > accu_val:
      scheduler.step()
      # save results, after 2 epochs
      if not os.path.isdir("./runs"):
          os.makedirs("runs")
      torch.save(model.state_dict(), "./runs/best" + "_" + "{:.3f}".format(accu_val) + ".pth")
    else:
       total_accu = accu_val
    print('-' * 59)
    print('| end of epoch {:3d} | time: {:5.2f}s | '
          'valid accuracy {:8.3f} '.format(epoch,
                                           time.time() - epoch_start_time,
                                           accu_val))
    print('-' * 59)


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

toPredict = [
    "안녕하세요",
    "네 좋은 아침이에요",
    "좀 있다 비온다던데, 우산 챙겼어요",
    "아니요, 비 많이 온데요?"
    ]

model = model.to("cpu")

for text in toPredict:
    print("-"*20)
    print(text)
    print("예측 : %s" %ag_news_label[predict(text, text_pipeline)])
    print("-" * 20)