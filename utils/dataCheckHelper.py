import glob
import os
import time

import keyboard

origin_path = "../augmented"
# text 가져오기
all_data = sorted(glob.glob(os.path.join(origin_path, "*.txt")))

ag_text_label = {
    0: "인사",
    1: "감사",
    2: "사과",
    3: "위급",
    4: "날씨"
}

for item in all_data:
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
    # 체크하고 삭제
    if len(text) < 8:
        print("-" * 20)
        print("label : ", ag_text_label[int(label)])
        print(text)
        print("-" * 20)
        print("press enter for delete, other for continue")
        keyboard.read_key()
        if keyboard.is_pressed('enter'):
            time.sleep(0.2)
            os.remove(item)
            print(item + " is removed")
        else:
            time.sleep(0.2)




