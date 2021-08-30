import glob
import os

from torch.utils.data import Dataset


class textDataset(Dataset):
  def __init__(self, data_dir):
    # 데이터 정의
    self.all_data = sorted(glob.glob(os.path.join(data_dir, "*", "*.txt")))

  def __getitem__(self, item):
    # 데이터 읽기
    data_path = self.all_data[item]  # 앞서 all_data에 저장된 경로들을 하나씩 data_path에 저장할수있음
    # 이 경우에는 파일이름.txt가 될것

    # 텍스트 읽기
    f = open(data_path, 'r', encoding='UTF-8')
    text = ""
    # 첫번째 줄은 label
    # strip() 함수는 문자열의 선행, 후행 개행 문자를 모두 제거
    label = f.readline().strip()
    # 두번째 줄 부터는 텍스트에 저장
    while True:
      line = f.readline()
      if not line: break
      text += line
    f.close()

    return label, text

  def __len__(self):
    length = len(self.all_data)
    return length