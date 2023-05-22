import os
import pandas as pd

# [회원정보] 폴더 안에 있는 txt 파일들을 읽어서 데이터프레임으로 변환하는 함수
def read_txt_files():
    data = []
    folder_path = '회원정보'
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.txt'):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r') as file:
                name = file.readline().split(': ')[1].strip()
                age = file.readline().split(': ')[1].strip()
                gender = file.readline().split(': ')[1].strip()
                email = file.readline().split(': ')[1].strip()
                data.append([name, age, gender, email])
    return data

# 데이터프레임을 엑셀 파일로 저장하는 함수
def save_to_excel(data):
    df = pd.DataFrame(data, columns=['이름', '나이', '성별', '이메일'])
    df.to_excel('회원정보.xlsx', index=False)

# [회원정보] 폴더 안에 있는 100개의 txt 파일을 하나의 엑셀 파일로 합치는 함수
def merge_txt_to_excel():
    data = read_txt_files()
    save_to_excel(data)

# [회원정보] 폴더 안에 있는 100개의 txt 파일을 하나의 엑셀 파일로 합침
merge_txt_to_excel()
print('텍스트 파일을 엑셀 파일로 합치는 작업이 완료되었습니다.')
