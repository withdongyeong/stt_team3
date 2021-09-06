import glob
import os

path = "./"
all_data = sorted(glob.glob(os.path.join(path, "*.txt")))

count = 0
for data in all_data:
    # 텍스트 읽기
    f = open(data, 'r')
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

    count +=1
    f = open("./" + "weather" + str(count).zfill(5) + ".txt", 'w', encoding='UTF-8')
    f.write(label + "\n")
    f.write(text)
    f.close()