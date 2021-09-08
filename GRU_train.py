import time

import torch
import os
from random import seed

import customDataset
from torch.utils.data import DataLoader, random_split
from torchtext.vocab import build_vocab_from_iterator
from konlpy.tag import Komoran

import nlpModel

BATCH_SIZE = 3
lr = 0.001
EPOCHS = 100

SEED = 5
# 랜덤함수 시드
seed(SEED)
# 토치 시드
torch.manual_seed(SEED)

# gpu 사용
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

dataPath = os.path.join(os.path.abspath('.'), 'conversationSet')
dataset = customDataset.TextDataset(dataPath)
num_train = int(len(dataset) * 0.8)
train_dataset, test_dataset = \
                random_split(dataset,[num_train, len(dataset) - num_train])


komoran = Komoran()


def yield_taken(data_iter):
    for _, text in data_iter:
        yield komoran.morphs(text)


vocab = build_vocab_from_iterator(yield_taken(train_dataset), specials=['<unk>'])
vocab.set_default_index(vocab['<unk>'])
print(vocab(['비','오늘','화창']))
# komoran에 의해 토큰화된 단어들이 어휘집에 들어가게 됨
# komoran의 식별률에 달려있는 부분
# 명사 식별률이 생각보다 낮은데, 최악의 경우엔 토크나이저를 쓰지 않고
# space 단위로 토큰화시켜야할듯함

# 텍스트처리 파이프라인은
# 데이터셋 반복자로부터 얻어온 가공되지 않은 문장 데이터를 처리할 떄 사용
# lambda 함수로 정의되어있어 text_pipeline(x) 와 같이 사용할 수 있음
# text_pipeline = lambda x: vocab(komoran.morphs(x))
# label_pipeline = lambda x: int(x)

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
        print(_text)
        label_list.append(label_pipeline(_label))
        processed_text = torch.tensor(text_pipeline(_text), dtype=torch.int64)
        text_list.append(processed_text)
        offsets.append(processed_text.size(0))
    label_list = torch.tensor(label_list, dtype=torch.int64)
    pre_offsets = torch.tensor(offsets)[:-1]
    offsets = torch.cumsum(pre_offsets, dim=0)
    text_list = torch.cat(text_list)
    return label_list.to(DEVICE), text_list.to(DEVICE), offsets.to(DEVICE)


    # print('origin', text_list)
    # text_list = torch.cat(text_list)
    # print('transformed', text_list)



dataLoader_train = DataLoader(train_dataset, batch_size=BATCH_SIZE,
                              shuffle=True, collate_fn=collate_batch)
dataLoader_test = DataLoader(test_dataset, batch_size=BATCH_SIZE,
                             shuffle=False, collate_fn=collate_batch)

n_classes = 5
vocab_size = len(vocab)
embeding_size = 64

model = nlpModel.BasicGRU(
    vocab_size= vocab_size,
    batch_size=BATCH_SIZE,
    embedding_dimension=embeding_size,
    hidden_size=128,
    n_layers=2,
    device=DEVICE,
    n_classes=n_classes
)
optimizer = torch.optim.SGD(model.parameters(), lr=lr)
criterion = torch.nn.CrossEntropyLoss()
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, 0.1, gamma=0.1)
total_accu = None


def train(model, optimizer, dataloader, criterion):
    model.to(DEVICE)
    model.train()
    total_acc, total_count = 0, 0
    log_interval = 500
    start_time = time.time()

    for idx, (label, text, offsets) in enumerate(dataloader):
        optimizer.zero_grad()
        predicted_label = model(text, offsets)
        exit()
        # print(label)
        # print(text)
        # # print(offsets)
        # predicted_label = model(text, offsets)
        # exit()

def evaluate(dataloader):
    pass
# model = nlpModel.BasicGRU(2, )

for epoch in range(1, EPOCHS + 1):
    epoch_start_time = time.time()
    train(model, optimizer, dataLoader_train, criterion)