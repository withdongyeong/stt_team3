import glob
import os

from tqdm import tqdm

from eda import *

def augmentation(text):
    # sr = 동의어 교체
    # ri = 임의 삽입
    # rs = 임의 스왑
    # rd = 임의 삭제
    # rs, rd만 사용하도록 변경해놓았음
    data = EDA(text, alpha_sr=0.05, alpha_ri=0.05, alpha_rs=0.05, p_rd=0.05, num_aug=16)
    data = set(data)
    return data

# 데이터 셋 가져오기
origin_path = "../conversationSet"
# text 가져오기
all_data = sorted(glob.glob(os.path.join(origin_path, "*", "*.txt")))

# make target dir
if not os.path.isdir("../augmented"):
    os.mkdir("../augmented")
target_path = "../augmented"

# 각 텍스트 데이터에 대해서
for item in tqdm(all_data):
    text = ""
    f = open(item, 'r', encoding='UTF-8')
    # 첫번째 줄은 label
    # strip() 함수는 문자열의 선행, 후행 개행 문자를 모두 제거
    label = f.readline().strip()
    # 두번째 줄 부터는 텍스트에 저장
    while True:
        line = f.readline()
        if not line: break
        text += line
    f.close()
    # text augmentation 진행
    data = augmentation(text)
    # augmented list
    for i, augmentedText in enumerate(data):
        index = i+1
        path = os.path.abspath(item)
        baseName = os.path.basename(path)
        fname = target_path + os.path.sep + baseName + "_" + "aug" + str(index).zfill(5) + ".txt"
        f = open(fname, 'w', encoding='UTF-8')
        f.write(label + '\n')
        f.write(augmentedText)
    f.close()