import glob
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Subset
from torchtext import data, datasets
import random
from sklearn.model_selection import ShuffleSplit

# 시드 고정
from stt_team3 import customDataset

SEED = 5
# 랜덤함수 시드
random.seed(SEED)
# 토치 시드
torch.manual_seed(SEED)

# 하이퍼 파라미터
BATCH_SIZE = 2
lr = 0.001
EPOCHS = 10

# gpu 사용
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 데이터셋을 만들고, 학습 및 테스트 데이터셋으로 분리
# 데이터셋 만들기
dataPath = "C:/Users/withd/Desktop/pythonProject1/test"
dataset = customDataset.textDataset(dataPath)

"""
sklearn의 ShuffleSplit
torch.utils.data의 Subset 함수를 사용할 것

작업 순서
1. dataset 생성
2. dataset의 길이만큼 인덱스 리스트를 만들고 인덱스를 셔플
3. 셔플된 인덱스를 통해 Subset으로 학습 및 테스트 데이터셋을 생성함
"""

# 셔플 객체 생성
# n_splits = 섞는 횟수
shuffle = ShuffleSplit(n_splits=1, test_size=0.2, random_state=SEED)
# dataset의 길이만큼 index 리스트를 만들고
indices = range(len(dataset))
# index를 셔플함
# shuffle.split은 Generator임
# 따라서 next를 사용하였고, 반복가능 횟수는 n_splits임
# 따라서 for 문으로 돌려도 됨
shuffledIndex = shuffle.split(indices)
train_index, test_index = next(shuffledIndex)

# 셔플된 index로 학습 및 테스트 데이터셋 생성
train_dataset = Subset(dataset, train_index)
test_dataset = Subset(dataset, test_index)