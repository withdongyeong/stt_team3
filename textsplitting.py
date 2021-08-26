import os


with open("origin.txt", encoding='UTF-8') as F:
    txt_read = F.read()
    or_name = 'stt_team3_00001.txt'
    count = 1
    for x in txt_read.split('\n'):
        if x not in ['0', '']:
            file_name = "stt_team3_{:05}.txt".format(count)
            count += 1

            print(x)
            print(file_name)
            file_opend = open('greetings/'+file_name, 'w', encoding='UTF-8')
            file_opend.write('0\n'+x)