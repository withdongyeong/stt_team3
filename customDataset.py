import glob
import os
from torch.utils.data import Dataset
from chardet import detect

class TextDataset(Dataset):

    def __init__(self, data_dir):
        self.all_data = sorted(glob.glob(os.path.join(data_dir, '*', '*')))

    def __getitem__(self, item):
        data_path = self.all_data[item]

        with open(data_path, 'r', encoding=self.find_codec(data_path)) as file:
            text = ''
            label = file.readline().strip()
            while True:
                line = file.readline()
                if not line:
                    break
                text += line

        return label, text

    def __len__(self):
        length = len(self.all_data)
        return length

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