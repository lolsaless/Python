import os
import pandas as pd

# [회원정보] 폴더 안에 있는 txt 파일들을 읽어서 데이터프레임으로 변환하는 함수
def read_txt_files():
    data_male = []
    data_female = []
    folder_path = '회원정보'
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.txt'):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r') as file:
                name = file.readline().split(': ')[1].strip()
                age = file.readline().split(': ')[1].strip()
                gender = file.readline().split(': ')[1].strip()
                email = file.readline().split(': ')[1].strip()
                if gender == '남':
                    data_male.append([name, age, gender, email])
                elif gender == '여':
                    data_female.append([name, age, gender, email])
    return data_male, data_female

# 데이터프레임을 엑셀 파일로 저장하는 함수
def save_to_excel(data_male, data_female):
    with pd.ExcelWriter('회원정보_남녀.xlsx') as writer:
        df_male = pd.DataFrame(data_male, columns=['이름', '나이', '성별', '이메일'])
        df_female = pd.DataFrame(data_female, columns=['이름', '나이', '성별', '이메일'])
        df_male.to_excel(writer, sheet_name='남자', index=False)
        df_female.to_excel(writer, sheet_name='여자', index=False)

# [회원정보] 폴더 안에 있는 100개의 txt 파일을 성별에 따라 '회원정보_남녀.xlsx' 파일에 sheet1에는 남자, sheet2에는 여자를 저장하는 함수
def separate_gender_to_excel():
    data_male, data_female = read_txt_files()
    save_to_excel(data_male, data_female)

# [회원정보] 폴더 안에 있는 100개의 txt 파일을 성별에 따라 '회원정보_남녀.xlsx' 파일에 sheet1에는 남자, sheet2에는 여자를 저장
separate_gender_to_excel()
print('텍스트 파일을 성별에 따라 회원정보_남녀.xlsx 파일에 저장하는 작업이 완료되었습니다.')
